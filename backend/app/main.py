import hashlib
import json
import secrets
import threading
import time
import uuid
from pathlib import Path
from pydantic import ValidationError

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import Settings
from .models import Incident, Approval, DocumentInput
from .providers import ProviderFactory
from .security import redact, injection_risk
from .store import Store, now
from .workflow import InvestigationWorkflow

ROOT = Path(__file__).resolve().parents[2]


def create_app(settings=None, providers=None):
    s = settings or Settings.from_env()
    store = Store(s.data_dir)
    p = providers or ProviderFactory(s, store)
    workflow = InvestigationWorkflow(s, store, p)
    app = FastAPI(title="Integration Hub", version="0.1.0")
    app.state.store, app.state.workflow, app.state.providers = store, workflow, p
    gate = threading.Lock()
    request_times = []
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver", "backend"])
    app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5180", "http://localhost:5180"],
                       allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type", "Authorization"])

    @app.middleware("http")
    async def protect(request: Request, call_next):
        from starlette.responses import JSONResponse
        if request.method == "OPTIONS": return await call_next(request)
        if s.api_token and not secrets.compare_digest(request.headers.get("authorization", ""), "Bearer " + s.api_token):
            return JSONResponse({"detail": "Authentication required"}, status_code=401)
        # Browser cross-site writes are blocked even in single-user local mode.
        origin = request.headers.get("origin")
        if origin and origin not in {"http://127.0.0.1:5180", "http://localhost:5180"}:
            return JSONResponse({"detail": "Origin not allowed"}, status_code=403)
        if int(request.headers.get("content-length", "0")) > 100000:
            return JSONResponse({"detail": "Request exceeds 100 KB limit"}, status_code=413)
        request.state.tenant = "local"  # Single-user scope; no client-supplied tenant impersonation.
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/health")
    def health(): return {"status": "ok", "profile": s.profile, "version": "0.1.0"}

    @app.get("/api/config")
    def config(): return {**s.public(), "providers": p.status()}

    @app.get("/api/dashboard")
    def dashboard():
        runs = store.list("run", "local")
        evaluations = store.list("evaluation", "local")
        return {"runs": runs, "documents": len(store.list("document", "local")), "tickets": store.list("ticket", "local"),
                "memory_count": len(store.list("memory", "local")), "evaluations": evaluations,
                "profile": s.profile, "generated_at": now()}

    def submit(fn):
        if not gate.acquire(blocking=False): raise HTTPException(429, "One investigation is already running")
        def guarded():
            try: fn()
            finally: gate.release()
        return guarded

    @app.post("/api/runs", status_code=202)
    def start(incident: Incident, tasks: BackgroundTasks):
        nonlocal request_times
        request_times = [t for t in request_times if time.monotonic() - t < 60]
        if len(request_times) >= 6: raise HTTPException(429, "Maximum six new runs per minute")
        id = uuid.uuid4().hex
        state = {"id": id, "tenant": "local", "incident": {k: redact(v) for k, v in incident.model_dump().items()},
                 "status": "running", "created_at": now(), "calls": [], "profile": s.profile}
        task = submit(lambda: workflow.run(state))
        request_times.append(time.monotonic())
        store.put("run", "local", id, state)
        tasks.add_task(task)
        return state

    @app.get("/api/runs/{id}")
    def run(id: str):
        result = store.get("run", "local", id)
        if not result: raise HTTPException(404, "Run not found")
        snapshot = workflow.graph.get_state(workflow.config("local", id))
        if result["status"] == "running" and snapshot.values:
            result = {**result, **snapshot.values}
        result["traces"] = list(reversed([t for t in store.list("trace", "local") if t["run_id"] == id]))
        return result

    @app.post("/api/runs/{id}/approval")
    def approve(id: str, approval: Approval, tasks: BackgroundTasks):
        current = store.get("run", "local", id)
        if not current: raise HTTPException(404, "Run not found")
        if current["status"] != "awaiting_approval": raise HTTPException(409, "Run is not awaiting approval")
        decision = approval.model_dump()
        decision["note"] = redact(decision["note"])
        task = submit(lambda: workflow.run(tenant="local", id=id, approval=decision))
        current["status"] = "running"
        store.put("run", "local", id, current)
        tasks.add_task(task)
        return {"status": "resuming"}

    @app.post("/api/runs/{id}/retry")
    def retry(id: str, tasks: BackgroundTasks):
        current = store.get("run", "local", id)
        if not current: raise HTTPException(404, "Run not found")
        if current["status"] not in {"failed", "running"}: raise HTTPException(409, "Only interrupted or failed runs can be retried")
        if current.get("profile") != s.profile: raise HTTPException(409, "Resume under the original profile to preserve data consent")
        task = submit(lambda: workflow.run(tenant="local", id=id))
        current.update(status="running", error="")
        store.put("run", "local", id, current)
        tasks.add_task(task)
        return {"status": "resuming"}

    @app.get("/api/documents")
    def documents(): return store.list("document", "local")

    def save_document(doc):
        if injection_risk(doc.text): raise HTTPException(422, "Document contains instruction-injection patterns; review it before ingestion")
        text = redact(doc.text)
        id = hashlib.sha256((doc.title + text).encode()).hexdigest()[:16]
        body = {"id": id, "title": doc.title, "text": text, "kind": doc.kind, "created_at": now()}
        store.put("document", "local", id, body)
        return body

    @app.post("/api/documents")
    def add_document(doc: DocumentInput): return save_document(doc)

    @app.post("/api/documents/upload")
    async def upload(file: UploadFile):
        if Path(file.filename or "").suffix.lower() not in {".txt", ".md", ".json"}:
            raise HTTPException(415, "Supported files: TXT, Markdown, JSON (including meeting exports)")
        content = await file.read(50001)
        if len(content) > 50000: raise HTTPException(413, "File exceeds 50 KB")
        try: text = content.decode("utf-8")
        except UnicodeDecodeError: raise HTTPException(422, "File must be UTF-8")
        try:
            doc = DocumentInput(title=Path(file.filename).name[:160], text=text)
        except ValidationError:
            raise HTTPException(422, "Document needs a title of at least 3 characters and at least 20 text characters")
        return save_document(doc)

    @app.post("/api/index/rebuild")
    def rebuild():
        if not gate.acquire(blocking=False): raise HTTPException(409, "Wait for the running investigation")
        try: return {"chunks": p.knowledge.rebuild("local")}
        finally: gate.release()

    @app.get("/api/memory")
    def memory(): return store.list("memory", "local")

    @app.delete("/api/memory/{id}")
    def forget(id: str):
        store.delete("memory", "local", id)
        return {"deleted": id}

    @app.get("/api/evaluations")
    def evaluations(): return store.list("evaluation", "local")

    @app.get("/api/runs/{id}/report", response_class=PlainTextResponse)
    def report(id: str):
        data = run(id)
        f = data.get("finding", {})
        lines = ["# " + data["incident"]["title"], "", "Status: " + data["status"], "Profile: " + data["profile"],
                 "", "## Hypothesis (requires operator verification)", f.get("hypothesis", "No supported finding"),
                 "", "Uncertainty: " + f.get("uncertainty", "Not assessed"), "", "## Evidence"]
        lines += [f"- [{c['source_id']}] {c['quote']}" for c in f.get("citations", [])]
        lines += ["", "## Proposed recovery"] + ["- " + x for x in f.get("recovery", [])]
        lines += ["", "## Provider provenance", "```json", json.dumps(data.get("calls", []), indent=2), "```"]
        return "\n".join(lines)

    @app.get("/api/samples")
    def samples(): return json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))

    return app
