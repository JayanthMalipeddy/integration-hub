from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Incident(StrictModel):
    title: str = Field(min_length=3, max_length=160)
    logs: str = Field(min_length=3, max_length=12000)
    service: str = Field(default="integration-api", min_length=1, max_length=80)


MAX_SEARCH_QUERY = 200
MAX_DECISION_REASON = 300


class Decision(StrictModel):
    tool: Literal["search_runbooks", "search_memory", "request_human"]
    query: str = Field(max_length=MAX_SEARCH_QUERY)
    reason: str = Field(max_length=MAX_DECISION_REASON)


class Citation(StrictModel):
    source_id: str
    quote: str = Field(min_length=8, max_length=500)


class Finding(StrictModel):
    category: Literal["authentication", "rate_limit", "timeout", "connection_pool", "database_storage", "authentication_load", "unknown"]
    hypothesis: str = Field(max_length=600)
    confidence: Literal["low", "medium", "high"]
    citations: list[Citation] = Field(max_length=4)
    checks: list[str] = Field(min_length=1, max_length=4)
    recovery: list[str] = Field(min_length=1, max_length=4)
    uncertainty: str = Field(max_length=400)


class Approval(StrictModel):
    approved: bool
    note: str = Field(default="", max_length=500)
    review_digest: str | None = Field(default=None, max_length=64)


class DocumentInput(StrictModel):
    title: str = Field(min_length=3, max_length=160)
    text: str = Field(min_length=20, max_length=50000)
    kind: Literal["runbook", "meeting", "api_spec"] = "runbook"


class EvidenceSubmission(StrictModel):
    text: str = Field(min_length=3, max_length=6000)
    expected_revision: int = Field(ge=1)
