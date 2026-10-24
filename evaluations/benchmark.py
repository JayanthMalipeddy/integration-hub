"""Real local benchmark with isolated checkpoints and explicitly simulated approvals."""
import hashlib
import json
import statistics
import time
import uuid
from dataclasses import replace
from pathlib import Path

from backend.app.config import Settings
from backend.app.providers import ProviderFactory, words
from backend.app.retrieval import INDEX_VERSION
from backend.app.security import redact
from backend.app.store import Store, now
from backend.app.workflow import InvestigationWorkflow
from evaluations.scoring import score_case
from scripts.seed import seed


ROOT = Path(__file__).resolve().parents[1]


def metric(values):
    values = [v for v in values if v is not None]
    return {"percent": round(100 * sum(values) / len(values), 2) if values else None,
            "passed": sum(values), "total": len(values)}


def metrics(rows):
    keys = ("task_passed", "category_correct", "tool_correct", "retrieval_hit_at_3",
            "expected_document_cited", "structured_output", "no_write_before_approval", "completion_passed")
    result = {key: metric([r[key] for r in rows]) for key in keys}
    result["citation_integrity"] = metric([c["valid"] for r in rows for c in r["citation_checks"]])
    return result


def evaluate():
    live = Settings.from_env()
    if live.profile != "local_free" or live.effective_vector_store != "chroma":
        raise ValueError("This benchmark requires local_free and Chroma; no paid calls are authorized by the harness")
    evaluation_id = "eval-" + uuid.uuid4().hex[:12]
    settings = replace(live, data_dir=live.data_dir / "evaluations" / evaluation_id)
    store = Store(settings.data_dir)
    seed(store)
    providers = ProviderFactory(settings, store)
    workflow = InvestigationWorkflow(settings, store, providers)
    # Unique server collection; do not index or modify the interactive workspace's data.
    tenant = evaluation_id
    for document in store.list("document", "local"):
        store.put("document", tenant, document["id"], document)
    cases, dataset_digest = [], hashlib.sha256()
    for filename, split in (("incidents.json", "baseline"), ("incidents_holdout.json", "holdout")):
        raw = (ROOT / "data" / filename).read_bytes()
        dataset_digest.update(raw)
        cases.extend({**c, "split": split} for c in json.loads(raw))
    providers.knowledge.rebuild(tenant)
    rows = []
    for case in cases:
        if providers.knowledge.health()["status"] != "ready":
            raise RuntimeError("Chroma became unavailable; partial results retained, no aggregate score published")
        run_id = uuid.uuid4().hex
        initial = {"id": run_id, "tenant": tenant, "incident": {k: redact(case[k]) for k in ("title", "service", "logs")},
                   "created_at": now(), "profile": settings.profile, "status": "running", "calls": []}
        started = time.perf_counter()
        result = workflow.run(initial)
        no_write = not store.get("ticket", tenant, "REC-" + run_id[:8]) and not store.get("memory", tenant, run_id)
        row = {"case": case["id"], "split": case["split"], "run_id": run_id, "status": result["status"],
               "expected_status": case["expected_status"], **score_case(case, result, no_write),
               "citation_checks": result.get("validation", {}).get("citations", []),
               "latency_ms": round((time.perf_counter() - started) * 1000, 2), "calls": result.get("calls", []),
               "analysis_attempts": result.get("analysis_attempts", 0), "error": result.get("error"),
               "finding": result.get("finding"), "decision": result.get("decision"), "completion_passed": None}
        # A test operator approves only successful proposals, in this isolated synthetic dataset.
        # This measures local completion mechanics, never human-rated RCA quality.
        if case["expected_document"]:
            row["completion_passed"] = False
            if row["task_passed"]:
                done = workflow.run(tenant=tenant, id=run_id, approval={"approved": True, "note": "Synthetic benchmark operator; not a real incident approval"})
                row["completion_passed"] = bool(done["status"] == "completed"
                    and store.get("ticket", tenant, "REC-" + run_id[:8]) and store.get("memory", tenant, run_id))
                row["completion_status"] = done["status"]
        rows.append(row)
        print(json.dumps({k: row[k] for k in ("case", "split", "status", "task_passed", "completion_passed", "analysis_attempts", "latency_ms")}), flush=True)
        (settings.data_dir / "progress.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    comparisons = []
    for case in cases:
        if not case["expected_document"]:
            continue
        # Alternate measurement order across repetitions; report embedding-inclusive latency.
        for repetition in range(3):
            modes = ("lexical", "vector") if repetition % 2 == 0 else ("vector", "lexical")
            for mode in modes:
                started = time.perf_counter()
                if mode == "vector":
                    ids = [d["document_id"] for d in providers.knowledge.search(tenant, case["logs"])]
                else:
                    docs = sorted(store.list("document", tenant), key=lambda d: -len(words(case["logs"]) & words(d["text"])))[:3]
                    ids = [d["id"] for d in docs]
                comparisons.append({"case": case["id"], "mode": mode, "repetition": repetition,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                    "hit_at_3": case["expected_document"] in ids,
                    "top1_correct": bool(ids and ids[0] == case["expected_document"]), "ids": ids})
    code_digest = hashlib.sha256()
    for path in sorted([*(ROOT / "backend/app").glob("*.py"), *(ROOT / "evaluations").glob("*.py")]):
        code_digest.update(path.relative_to(ROOT).as_posix().encode())
        code_digest.update(path.read_bytes())
    report = {"id": evaluation_id, "timestamp": now(), "profile": settings.profile, "model": settings.model,
              "dataset_version": dataset_digest.hexdigest(), "dataset_size": len(cases), "code_version": code_digest.hexdigest(),
              "configuration": {"embedding_model": settings.embed_model, "index_version": INDEX_VERSION,
                                "chroma_mode": settings.chroma_mode, "chroma_endpoint": settings.public()["chroma_endpoint"],
                                "max_corrections": settings.max_corrections, "max_steps": settings.max_steps},
              "metrics": metrics(rows), "split_metrics": {split: metrics([r for r in rows if r["split"] == split]) for split in ("baseline", "holdout")},
              "mean_latency_ms": round(statistics.mean(r["latency_ms"] for r in rows), 2),
              "total_tokens": sum((c.get("input_tokens") or 0) + (c.get("output_tokens") or 0) for r in rows for c in r["calls"]),
              "approximate_api_cost_usd": sum(c.get("cost_usd") or 0 for r in rows for c in r["calls"]),
              "results": rows, "retrieval_comparison": comparisons,
              "approval_mode": "simulated operator in isolated synthetic evaluation storage",
              "not_measured": ["semantic claim entailment", "human-rated RCA usefulness", "production incident accuracy", "live paid-provider interoperability"],
              "other_profiles": {p: "not_run" for p in ("hybrid", "sponsored")},
              "limitations": "18 synthetic cases (6 baseline, 12 newly authored holdout); one workflow run each. The original holdout split is retained for historical comparison, but those cases are now known development regressions after feedback-driven planner changes; they are not independent unseen validation. Four runbooks. Retrieval has three order-alternated repetitions per query; vector timing includes local embeddings and HTTP. Completion uses simulated approvals. Exact quotes do not prove semantic support. Hardware/electricity excluded."}
    output = ROOT / "evaluations/results" / (evaluation_id + ".json")
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    # Publish only the result summary. Evaluation tickets, memory and checkpoints stay isolated.
    Store(live.data_dir).put("evaluation", "local", evaluation_id, report)
    print(json.dumps({"id": evaluation_id, "metrics": report["metrics"], "split_metrics": report["split_metrics"]}), flush=True)
    return report


if __name__ == "__main__":
    evaluate()
