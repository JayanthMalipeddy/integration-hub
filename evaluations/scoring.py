"""Deterministic task rubric, separate from model generation and UI presentation."""


def score_case(case, result, no_write):
    expected_doc = case["expected_document"]
    evidence = result.get("evidence", [])
    finding = result.get("finding", {})
    retrieved = [e.get("document_id") for e in evidence]
    cited = {c["source_id"] for c in finding.get("citations", [])}
    expected_cited = any(e.get("document_id") == expected_doc and e["id"] in cited for e in evidence) if expected_doc else None
    tool_correct = result.get("decision", {}).get("tool") == case["expected_tool"] if case["expected_tool"] else None
    hit = expected_doc in retrieved if expected_doc else None
    category_correct = finding.get("category") == case["expected_category"] if expected_doc else None
    passed = (result["status"] == case["expected_status"] and no_write
              and tool_correct is not False and (not expected_doc or
              (category_correct and hit and expected_cited and result.get("validation", {}).get("passed", False))))
    return {"task_passed": bool(passed), "category_correct": category_correct,
            "tool_correct": tool_correct, "retrieval_hit_at_3": hit,
            "expected_document_cited": expected_cited, "retrieved_documents": retrieved,
            "structured_output": bool(finding) if expected_doc else None,
            "no_write_before_approval": no_write,
            "reciprocal_rank": 1 / (retrieved.index(expected_doc) + 1) if hit else 0 if expected_doc else None}
