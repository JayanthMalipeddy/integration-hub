"""Planner routing regressions; fixture outcomes are not model accuracy measurements."""
import pytest

from tests.test_workflow import FixtureLLM, build, state


class PlannerLLM(FixtureLLM):
    def __init__(self, tool):
        self.tool = tool
        self.requests = []

    def generate(self, messages, schema):
        self.requests.append(schema["title"])
        assert schema["title"] == "Decision", "Handoff or empty retrieval must skip analysis"
        result = super().generate(messages, schema)
        result["content"] = {"tool": self.tool, "query": "" if self.tool == "request_human" else "connection failure",
                             "reason": "Please supply the failing request trace."}
        return result


class EmptyKnowledge:
    def __init__(self):
        self.queries = []

    def search(self, tenant, query):
        self.queries.append(query)
        return []


def test_blank_logs_skip_model_retrieval_and_writes(tmp_path):
    llm = PlannerLLM("search_runbooks")
    knowledge = EmptyKnowledge()
    _, store, _, flow = build(tmp_path, llm=llm, knowledge=knowledge)
    result = flow.run(state("  \n\t "))
    assert result["status"] == "needs_human"
    assert result["decision"]["tool"] == "request_human"
    assert result["error"] == result["decision"]["reason"]
    assert not llm.requests and not knowledge.queries and not result["calls"]
    assert not store.list("ticket", "local") and not store.list("memory", "local")


def test_model_handoff_skips_retrieval_and_analysis(tmp_path):
    llm = PlannerLLM("request_human")
    knowledge = EmptyKnowledge()
    _, store, _, flow = build(tmp_path, llm=llm, knowledge=knowledge)
    result = flow.run(state("The user reports trouble but has supplied no telemetry."))
    assert result["status"] == "needs_human"
    assert llm.requests == ["Decision"] and not knowledge.queries
    assert result["error"] == "Please supply the failing request trace."
    assert not store.list("ticket", "local") and not store.list("memory", "local")


@pytest.mark.parametrize("logs", [
    "socket error=ECONNRESET peer closed connection during upload",
    "worker error=ZXQ912 payload rejected by custom adapter",
    'response status=200 body={"success":false,"error":"order validation failed"}',
    "response duration_ms=18000 exceeds expected maximum=1000ms",
    "ConnectionResetError: connection closed; no request trace was captured",
])
def test_unrecognized_failure_can_reach_retrieval(tmp_path, logs):
    llm = PlannerLLM("search_runbooks")
    knowledge = EmptyKnowledge()
    _, store, _, flow = build(tmp_path, llm=llm, knowledge=knowledge)
    result = flow.run(state(logs))
    assert result["signals"]["categories"] == []
    assert llm.requests == ["Decision"] and len(knowledge.queries) == 1
    assert result["status"] == "needs_human"  # Empty fixture retrieval, not a triage veto.
    assert result["error"] == "Insufficient evidence; operator investigation required"
    assert not store.list("ticket", "local")


@pytest.mark.parametrize("logs", ["   ", "No current logs are available."])
def test_explicit_history_request_reaches_memory_without_current_error(tmp_path, logs):
    llm = PlannerLLM("search_memory")
    _, store, providers, flow = build(tmp_path, llm=llm)
    queries = []
    providers.memory.retrieve = lambda tenant, query: queries.append(query) or []
    initial = state(logs)
    initial["incident"]["title"] = "Find previous incidents involving the billing adapter"
    result = flow.run(initial)
    assert result["decision"]["tool"] == "search_memory"
    assert llm.requests == ["Decision"] and len(queries) == 1
    assert not store.list("ticket", "local")
