from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Incident(StrictModel):
    title: str = Field(min_length=3, max_length=160)
    logs: str = Field(min_length=3, max_length=12000)
    service: str = Field(default="integration-api", min_length=1, max_length=80)


class Decision(StrictModel):
    tool: Literal["search_runbooks", "search_memory", "request_human"]
    query: str = Field(max_length=200)
    reason: str = Field(max_length=300)


class Citation(StrictModel):
    source_id: str
    quote: str = Field(min_length=8, max_length=500)


class Finding(StrictModel):
    category: Literal["authentication", "rate_limit", "timeout", "connection_pool", "unknown"]
    hypothesis: str = Field(max_length=600)
    confidence: Literal["low", "medium", "high"]
    citations: list[Citation] = Field(max_length=4)
    checks: list[str] = Field(min_length=1, max_length=4)
    recovery: list[str] = Field(min_length=1, max_length=4)
    uncertainty: str = Field(max_length=400)


class Approval(StrictModel):
    approved: bool
    note: str = Field(default="", max_length=500)


class DocumentInput(StrictModel):
    title: str = Field(min_length=3, max_length=160)
    text: str = Field(min_length=20, max_length=50000)
    kind: Literal["runbook", "meeting", "api_spec"] = "runbook"
