"""Regression coverage for verbose planner responses on manually supplied incidents.
All stores are temporary and providers are fixtures; these are not model benchmarks.
"""
import pytest

from backend.app.models import Decision
from backend.app.security import redact_data
from backend.app.planning import compact_query, prepare_decision
from tests.test_planner import EmptyKnowledge
from tests.test_workflow import FixtureLLM, build, state, LOG

# Anonymized operational example; no customer names, accounts or network addresses.
REALISTIC_LOG = """2026-08-25 11:48 - Production API consumers receive HTTP 408 Request Timed Out.
2026-08-25 12:04 - JDBC pool oracle:internal -> connection not available (error code 107).
Many concurrent calls from the same client hit submitCompany -> updateEmployee.
Thread dump: 750+ server threads busy in Basic Authentication password verification (PBKDF2).
CPU on the IS nodes: saturated (95%+). All services are slow."""
VERBOSE_QUERY = ("408 request timeouts, Oracle-backed API calls, service chain issues, "
                 "many concurrent requests and unavailable connections, investigation of "
                 "the production Integration Server and repeated client requests; "
                 "PBKDF2 JDBC CPU error 107")


class DecisionLLM(FixtureLLM):
    def __init__(self, content):
        self.content = content
        self.requests = []

    def generate(self, messages, schema):
        self.requests.append(schema["title"])
        result = super().generate(messages, schema)
        if schema["title"] == "Decision":
            result["content"] = self.content
        return result


def decision(query=VERBOSE_QUERY, **overrides):
    return {"tool": "search_runbooks", "query": query, "reason": "Find relevant diagnostic guidance", **overrides}


def test_reported_scenario_reaches_retrieval_without_losing_original_evidence(tmp_path):
    llm = DecisionLLM(decision())
    knowledge = EmptyKnowledge()
    _, store, _, flow = build(tmp_path, llm=llm, knowledge=knowledge)
    initial = state(REALISTIC_LOG)
    result = flow.run(initial)
    assert len(VERBOSE_QUERY) > 200
    assert result["status"] == "needs_human"  # No runbook fixture: no invented diagnosis.
    assert len(knowledge.queries) == 1 and 0 < len(knowledge.queries[0]) <= 200
    for term in ("408", "PBKDF2", "JDBC", "CPU", "error 107"):
        assert term in knowledge.queries[0]
    assert result["incident"] == redact_data(initial["incident"])  # Existing secret redaction still applies.
    assert llm.requests == ["Decision"]  # No extra model call or token spend for compaction.
    assert result["calls"][0]["input_tokens"] == 20
    assert any(t.get("adjusted_fields") == ["query"] for t in store.list("trace", "local"))
    assert not store.list("ticket", "local") and not store.list("memory", "local")


def test_long_query_still_allows_verified_workflow_to_reach_approval(tmp_path):
    llm = DecisionLLM(decision("authentication expired token " * 20 + "401"))
    _, store, _, flow = build(tmp_path, llm=llm)
    result = flow.run(state(LOG))
    assert result["status"] == "awaiting_approval"
    assert result["validation"]["passed"]
    assert llm.requests == ["Decision", "Finding"]
    assert not store.list("ticket", "local")


@pytest.mark.parametrize("content", [
    decision(tool="execute_shell"), decision(query=123), decision(query=None),
    decision(query="   "), decision(query="x" * 250), decision(reason=None),
    {"tool": "search_runbooks"}, decision(unexpected="extra"), ["not an object"],
])
def test_unusable_decision_hands_off_and_records_usage_without_retrieval(tmp_path, content):
    llm = DecisionLLM(content)
    knowledge = EmptyKnowledge()
    _, store, _, flow = build(tmp_path, llm=llm, knowledge=knowledge)
    result = flow.run(state(REALISTIC_LOG))
    assert result["status"] == "needs_human"
    assert result["decision"]["tool"] == "request_human"
    assert "valid search request" in result["error"] and "validation error" not in result["error"]
    assert len(result["calls"]) == 1 and result["calls"][0]["output_tokens"] == 30
    assert not knowledge.queries and not store.list("ticket", "local")


@pytest.mark.parametrize("query", ["x" * 199, "x" * 200, "401 invalid_token"])
def test_in_limit_query_is_unchanged(query):
    content = decision(query)
    prepared, adjusted = prepare_decision(content)
    assert prepared == content and not adjusted
    assert Decision.model_validate(prepared).query == query


def test_codes_at_end_survive_and_unicode_stays_within_character_limit():
    query = "database allocation investigation " * 20 + "ORA-01653 ORA-01691 PBKDF2 " + "?? " * 80
    bounded = compact_query(query)
    assert len(bounded) <= 200
    assert all(term in bounded for term in ("ORA-01653", "ORA-01691", "PBKDF2"))
    assert bounded == compact_query(query)


def test_handoff_discards_query_and_long_reason_is_bounded_without_mutating_input(tmp_path):
    original = decision(tool="request_human", reason="Request more information. " * 30)
    prepared, adjusted = prepare_decision(original)
    assert prepared["query"] == "" and len(prepared["reason"]) <= 300
    assert original["query"] == VERBOSE_QUERY
    assert adjusted == ["query", "reason"]
    knowledge = EmptyKnowledge()
    _, _, _, flow = build(tmp_path, llm=DecisionLLM(original), knowledge=knowledge)
    assert flow.run(state(REALISTIC_LOG))["status"] == "needs_human"
    assert not knowledge.queries
