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
from fastapi.responses import PlainTextResponse, Response
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import Settings
from .models import Incident, Approval, DocumentInput, EvidenceSubmission
from .providers import ProviderFactory
from .security import redact, injection_risk, redact_data
from .operations import Operations
from .request_limits import RequestLimitMiddleware
from .store import Store, now
from .workflow import InvestigationWorkflow
from .evidence import evidence_digest
from .provenance import fingerprints, freshness
from .reports import DOCX_MEDIA_TYPE, investigation_docx, report_filename

ROOT = Path(__file__).resolve().parents[2]


def create_app(settings=None, providers=None):
    s = settings or Settings.from_env()
    if s.require_auth and not s.api_token:
        raise ValueError("API_TOKEN is required. Run python -m scripts.configure_access before starting the API.")
    store = Store(s.data_dir)
    p = providers or ProviderFactory(s, store)
    workflow = InvestigationWorkflow(s, store, p)
    app = FastAPI(title="Integration Hub", version="0.1.0")
    app.state.store, app.state.workflow, app.state.providers = store, workflow, p
    loaded_fingerprints = fingerprints()
    gate = threading.Lock()
    request_times = []
    request_lock = threading.Lock()
    operations = Operations()
    app.add_middleware(RequestLimitMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver", "backend"])
    app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5180", "http://localhost:5180"],
                       allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type", "Authorization"])

    @app.middleware("http")
    async def protect(request: Request, call_next):
        from starlette.responses import JSONResponse
        started = time.perf_counter()
        response = None
        try:
            origin = request.headers.get("origin")
            if origin and origin not in {"http://127.0.0.1:5180", "http://localhost:5180"}:
                response = JSONResponse({"detail": "Origin not allowed"}, status_code=403)
            elif request.method != "OPTIONS" and s.api_token and not secrets.compare_digest(
                    request.headers.get("authorization", "").encode(), ("Bearer " + s.api_token).encode()):
                response = JSONResponse({"detail": "Authentication required"}, status_code=401,
                                        headers={"WWW-Authenticate": "Bearer"})
            else:
                request.state.tenant = "local"
                response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Cache-Control"] = "no-store"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "no-referrer"
            return response
        finally:
            operations.record(response.status_code if response else 500, (time.perf_counter() - started) * 1000)

    @app.get("/api/health")
    def health(): return {"status": "ok", "profile": s.profile, "version": "0.1.0"}

    @app.get("/api/ready")
    def ready():
        from starlette.responses import JSONResponse
        try:
            with store.lock:
                store.db.execute("SELECT 1").fetchone()
            providers_status = p.status()
            checks = {name: providers_status.get(name, {}).get("status") == "ready"
                      for name in ("llm", "embeddings", "vector_store")}
            checks["database"] = True
        except Exception:
            checks = {"dependencies": False}
        healthy = all(checks.values())
        return JSONResponse({"status": "ready" if healthy else "degraded", "checks": checks},
                            status_code=200 if healthy else 503)

    @app.get("/api/operations")
    def operation_status():
        metrics = operations.snapshot()
        runs = store.list("run", "local")
        failed = sum(run.get("status") == "failed" for run in runs)
        alerts = []
        if not s.api_token:
            alerts.append("Authentication is disabled for this development instance.")
        if metrics["status_counts"].get("401", 0):
            alerts.append("Authentication requests have been rejected since startup.")
        if any(int(code) >= 500 for code in metrics["status_counts"]):
            alerts.append("Server or readiness failures have occurred since startup.")
        if failed:
            alerts.append(f"{failed} saved investigations need failure review or retry.")
        return {**metrics, "failed_runs": failed, "running_runs": sum(r.get("status") == "running" for r in runs),
                "alerts": alerts, "limits": {"active_investigations": 1, "new_runs_per_minute": 6},
                "note": "Request latency measures API handling, not background model inference. Review workflow traces for model timings."}

    @app.get("/api/config")
    def config(): return {**s.public(), "providers": p.status()}

    @app.get("/api/dashboard")
    def dashboard():
        runs = store.list("run", "local")
        evaluations = [{**r, "freshness": freshness(r, loaded_fingerprints)} for r in store.list("evaluation", "local")]
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
        with request_lock:
            request_times = [t for t in request_times if time.monotonic() - t < 60]
            if len(request_times) >= 6: raise HTTPException(429, "Maximum six new runs per minute")
            request_times.append(time.monotonic())
        id = uuid.uuid4().hex
        state = {"id": id, "tenant": "local", "incident": {k: redact(v) for k, v in incident.model_dump().items()},
                 "status": "running", "created_at": now(), "calls": [], "profile": s.profile,
                 "evidence_revision": 1, "evidence_history": []}
        task = submit(lambda: workflow.run(state))
        store.put("run", "local", id, state)
        tasks.add_task(task)
        return state

    @app.get("/api/runs/{id}")
    def run(id: str):
        result = store.get("run", "local", id)
        if not result: raise HTTPException(404, "Run not found")
        snapshot = workflow.graph.get_state(workflow.config("local", id))
        if result["status"] == "running" and snapshot.values:
            result = {**result, **redact_data(snapshot.values)}
        result["traces"] = list(reversed([t for t in store.list("trace", "local") if t["run_id"] == id]))
        return result

    @app.post("/api/runs/{id}/approval")
    def approve(id: str, approval: Approval, tasks: BackgroundTasks):
        current = store.get("run", "local", id)
        if not current: raise HTTPException(404, "Run not found")
        if current["status"] != "awaiting_approval": raise HTTPException(409, "Run is not awaiting approval")
        if approval.approved and current.get("review_digest") and approval.review_digest != current["review_digest"]:
            raise HTTPException(409, "The displayed review is missing or stale. Refresh and review the current evidence.")
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

    @app.post("/api/runs/{id}/evidence", status_code=202)
    def add_evidence(id: str, submission: EvidenceSubmission, tasks: BackgroundTasks):
        current = store.get("run", "local", id)
        if not current:
            raise HTTPException(404, "Run not found")
        if current["status"] not in {"needs_human", "failed", "awaiting_approval"}:
            raise HTTPException(409, "Evidence can be added only to an investigation awaiting review or follow-up")
        if current.get("profile") != s.profile:
            raise HTTPException(409, "Continue under the original provider profile to preserve data consent")
        revision = current.get("evidence_revision", 1)
        if submission.expected_revision != revision:
            raise HTTPException(409, "Evidence changed. Refresh before submitting another revision")
        if revision >= 5:
            raise HTTPException(409, "Five evidence revisions reached; export this record and request operator review")
        text = redact(submission.text).strip()
        if len(text) < 3 or injection_risk(text):
            raise HTTPException(422, "Provide factual evidence or an unavailable-evidence explanation without instructions to the agent")
        combined = current["incident"]["logs"] + f"\n\nOperator evidence revision {revision + 1}:\n" + text
        if len(combined) > 12000:
            raise HTTPException(422, "Combined evidence exceeds 12,000 characters. Provide a shorter factual addition; previous evidence will not be discarded")
        history = current.get("evidence_history", []) + [{
            "revision": revision, "incident": current["incident"], "finding": current.get("finding"),
            "validation": current.get("validation"), "status": current["status"], "recorded_at": now(),
            "digest": evidence_digest(current["incident"])}]
        updated = {**current, "incident": {**current["incident"], "logs": combined},
                   "evidence_revision": revision + 1, "evidence_history": history,
                   "budget_call_offset": len(current.get("calls", [])), "analysis_attempts": 0,
                   "status": "running", "error": "", "finding": {}, "draft_finding": {}, "validation": {},
                   "decision": {}, "evidence": [], "schema_error": "", "unsafe_evidence": False,
                   "approved": False, "approval_note": "", "review_digest": "", "source_versions": {},
                   "questions": [], "context_coverage": {}, "ticket_id": ""}
        task = submit(lambda: workflow.run(updated))
        store.put("run", "local", id, updated)
        tasks.add_task(task)
        return {"id": id, "status": "running", "evidence_revision": revision + 1}

    @app.get("/api/documents")
    def documents(): return store.list("document", "local")

    def save_document(doc):
        if injection_risk(doc.title + "\n" + doc.text): raise HTTPException(422, "Document contains instruction-injection patterns; review it before ingestion")
        text, title = redact(doc.text), redact(doc.title)
        id = hashlib.sha256((title + text).encode()).hexdigest()[:16]
        body = {"id": id, "title": title, "text": text, "kind": doc.kind, "created_at": now()}
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
    def evaluations(): return [{**r, "freshness": freshness(r, loaded_fingerprints)} for r in store.list("evaluation", "local")]

    @app.get("/api/runs/{id}/report.docx")
    def word_report(id: str):
        data = run(id)
        return Response(content=investigation_docx(data), media_type=DOCX_MEDIA_TYPE,
                        headers={"Content-Disposition": f'attachment; filename="{report_filename(id)}"'})

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
        return redact("\n".join(lines))

    @app.get("/api/samples")
    def samples(): return json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))

    return app
