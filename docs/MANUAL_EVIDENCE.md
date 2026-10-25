# Manual evidence and bounded investigation

Integration Hub accepts what the operator can supply. It does not connect to production databases, read server log files or claim to confirm a root cause from a symptom alone.

## Investigation flow

1. Submit a title, affected service and sanitized observations/log excerpts. The combined evidence limit is 12,000 characters.
2. The planner selects an allowlisted read tool. Runbooks are admitted only when their declared/recognized domain overlaps an observed signal. No matching domain produces a handoff.
3. The model selects a category and exact quotations. Existing schema/citation repair remains bounded. Its free-form causal prose is retained as an unverified draft in the record; it is not promoted into the accepted summary or recovery ticket.
4. Accepted observations are rendered from exact supplied excerpts with line IDs. Next steps come from cited runbook guidance or a conservative request for missing evidence. This is an evidence review, not an automated causal verdict.
5. In Investigation detail, use **Add evidence and continue** to supply answers, conflicting observations, or an explanation that data is unavailable. The same investigation ID is retained, with a new evidence revision and the previous incident/finding/validation snapshot.
6. A new revision invalidates the previous approval proposal. The server rejects submissions against an old revision and approvals against an old review digest. At most five evidence revisions are accepted; each explicit revision gets a new bounded inference allowance while prior call usage remains in the record.
7. Approval creates only a local ticket and reviewed, unverified memory. Canonical source records are checked again after the approval pause. If any changed or disappeared, no completion writes occur and the operator must review updated evidence.
8. Word export includes observed excerpts, outstanding questions and the evidence revision.

## What to provide

- Incident time/timezone, affected node/service and scope.
- Exact errors and timestamps, with credentials/customer identifiers removed.
- Which observations came from the same node and time window.
- Request counts, CPU/thread summaries, pool metrics or DBA findings only if available.
- Recent changes, contradictory findings and explicitly unavailable details.

Do not supply secrets or give the agent direct administrative access. A report from the DBA is sufficient evidence input; database credentials are unnecessary.

## Domain boundaries

The shipped corpus covers authentication rejection, rate limiting, timeouts, connection acquisition, Oracle segment allocation and authentication workload. The last two guides are conservative investigation guidance, based on [Oracle's ORA-01653 explanation](https://docs.oracle.com/en/error-help/db/ora-01653/) and [IBM's Basic Authentication documentation](https://www.ibm.com/docs/en/webmethods-integration/wm-integration-server/11.1.0?topic=clients-basic-authentication). Their presence does not establish that a particular incident has that cause. An observed Oracle allocation failure is not proof of pool exhaustion; PBKDF2 stacks and high CPU do not prove why traffic grew.

Unknown domains are handed off rather than forced into a known category. A source domain match is an admission rule, not a semantic relevance score. Custom runbooks still require operator review.

## Context and budget semantics

Selection scans all submitted lines and prioritizes distinct diagnostic signals, so a late error is not automatically discarded by a prefix slice. The UI explicitly labels selected excerpts and retains the full supplied evidence. It does not claim every line reached the model. Contradictions still require operator interpretation.

The pre-call guard uses a conservative UTF-8 byte upper bound for the selected prompt plus schema/output reserve, and recorded token usage for completed calls. Bytes are not reported as consumed tokens. If the request cannot safely fit, the investigation enters `needs_human`, retains evidence and requests focused details. No tokenizer package was installed and no exact model-tokenizer guarantee is claimed.

## API changes

- `POST /api/runs/{id}/evidence`: `{ "text": "sanitized additional findings", "expected_revision": 1 }`; returns 202. Valid on needs_human, failed or awaiting_approval; profile must remain unchanged. Concurrent/stale submissions are rejected.
- `POST /api/runs/{id}/approval`: include the displayed `review_digest` for approval. The frontend supplies it automatically. A missing/stale digest on a new proposal returns 409.
- New run fields include observations, questions, evidence_revision, evidence_history, context_coverage, source_versions and review_digest. Existing status/citation/report routes remain available.
- Historical proposals without the new evidence contract must be reassessed; they are not automatically grandfathered into valid diagnoses.

## Verification

`tests/test_gap_repairs.py` covers unsupported causes/actions, Oracle domain separation, late evidence, stale/withdrawn sources, irrelevant retrieval, budget handoff, manual revisions, stale approvals, privacy precision, partial completion recovery and offline checkpoint restoration. These are deterministic regression tests with temporary stores and explicit fixtures, not model accuracy scores.
