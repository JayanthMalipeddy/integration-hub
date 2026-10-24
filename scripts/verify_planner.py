"""Measure tool selection on separate boundary cases; not a full workflow benchmark."""
import hashlib
import json
import time
import uuid
from dataclasses import replace
from pathlib import Path

from backend.app.config import Settings
from backend.app.providers import ProviderFactory
from backend.app.store import Store, now
from backend.app.workflow import InvestigationWorkflow

ROOT = Path(__file__).resolve().parents[1]


def verify():
    live = Settings.from_env()
    if live.profile != "local_free":
        raise ValueError("Planner verification requires local_free; no paid calls")
    identifier = "planner-" + uuid.uuid4().hex[:12]
    settings = replace(live, data_dir=live.data_dir / "evaluations" / identifier)
    store = Store(settings.data_dir)
    workflow = InvestigationWorkflow(settings, store, ProviderFactory(settings, store))
    raw = (ROOT / "data/planner_checks.json").read_bytes()
    code_hash = hashlib.sha256((ROOT / "backend/app/workflow.py").read_bytes()).hexdigest()
    rows = []
    try:
        for case in json.loads(raw):
            state = {"id": uuid.uuid4().hex, "tenant": identifier, "calls": [],
                     "incident": {"title": case["title"], "logs": case["logs"], "service": "synthetic"}}
            started = time.perf_counter()
            state.update(workflow.triage(state))
            result = workflow.plan(state)
            rows.append({"case": case["id"], "expected_tool": case["expected_tool"],
                         "decision": result["decision"], "calls": result["calls"],
                         "passed": result["decision"]["tool"] == case["expected_tool"],
                         "latency_ms": round(1000 * (time.perf_counter() - started), 2)})
            (settings.data_dir / "progress.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
            print(json.dumps(rows[-1]), flush=True)
        report = {"id": identifier, "timestamp": now(), "model": settings.model,
                  "dataset_sha256": hashlib.sha256(raw).hexdigest(), "workflow_sha256": code_hash,
                  "passed": sum(row["passed"] for row in rows), "total": len(rows), "results": rows,
                  "scope": "Planner-only boundary checks authored for this change, one run each. No retrieval, analysis or approval executed. Separate from the 18-case workflow benchmark; not independent accuracy evidence."}
        (ROOT / "evaluations/results" / (identifier + ".json")).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({k: report[k] for k in ("id", "passed", "total")}), flush=True)
        return report
    finally:
        workflow.connection.close()
        store.db.close()


if __name__ == "__main__":
    verify()
