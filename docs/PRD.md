# Product requirements and acceptance

**One-liner:** My agent helps integration support engineers investigate API failures in a browser workspace, replacing manual log/runbook correlation. It parses logs and chooses between two read-only tools, drafts a cited recovery plan, and hands off whenever evidence is missing or before creating a recovery ticket. Success is a reviewable, evidence-backed investigation with zero unapproved writes; time is measured per run.

## Scope

- Users: one local support engineer, with a future team deployment path.
- Input: sanitized log excerpts and UTF-8 runbooks/API specifications/meeting exports.
- Output: categorized observations, exact source quotes, unverified-cause status, follow-up questions, source-backed next steps, trace and optional approved local ticket.
- Core surfaces: overview, agent workspace, knowledge, incidents, RCA, timeline, evaluations, provider configuration, memory, exports and settings.
- Deterministic code handles parsing, budgets, validation, authorization, storage, metrics and ticket writes. Model reasoning is limited to read-only tool selection and investigation synthesis.

## Acceptance status

| Requirement | Evidence/status |
|---|---|
| No paid keys required | Real LOCAL_FREE Ollama workflow executed |
| Agent chooses a tool | Decision schema and conditional LangGraph routing; real outputs retained |
| Persistent state and human approval | SQLite checkpointer; restart/resume, rejection and duplicate approval tests |
| Traceable retrieval | Chroma + local embeddings; source IDs/quotes, canonical-source validation |
| Errors and uncertainty | Bounded retries, circuit breaker, saved failures/retry, insufficient-evidence handoff |
| Provider-independent core | One central factory; real local adapter and contract-tested cloud adapters |
| One profile selector | LOCAL_FREE/HYBRID/SPONSORED mappings; credentials/consent still required |
| Local frontend | React/TypeScript build passed; HTTP service available on 5180 |
| Evaluation evidence | Current frozen 24-case regression harness and raw artifacts; historical 6/18-case results retained; diagnostic accuracy not measured |
| Portability | Canonical SQLite, backup/restore and index rebuild; restore tested |
| Cloud interoperability | Adapter contracts tested; live credentials and service-side limits pending |
| Docker | Compose syntax valid; engine was unavailable for a container run |
| Optional local voice | Disabled; no Whisper/Piper installation performed |
| Production rollout | Not claimed: SSO/RBAC, retention, encryption and operational review remain |

## Milestones

1. Foundation: independent folder, API/UI, provider protocols, canonical storage, real Ollama call.
2. Investigation: graph, runbooks, semantic retrieval, citation verification, approval and checkpoints.
3. Portability: central profiles, cloud adapters with disabled-by-default consent gates, backup and explicit external synchronization.
4. Verification: tests, actual local evals, live dashboard and submission documentation.

Out of scope for this submission: running shell commands, production restarts, transaction replay, autonomous external messages, paid deployment, recording meetings, and unsupported claims of production readiness.

## Measurable targets and evidence lifecycle

Targets for the current local CPU demonstration: p95 first review/handoff within six minutes for the shipped regression workload; vague-input handoff within 30 seconds; zero pre-approval action writes; all accepted primary observations tied to supplied excerpts. These are targets to compare with recorded runs, not guaranteed SLAs. Manual troubleshooting time has not been measured, so no time-saving percentage is claimed.

Evidence is manually supplied and versioned (at most five revisions); prior snapshots remain reviewable in the stored run. Reviewed memory is retained until an operator explicitly forgets it. Memory is labelled unverified and must never be treated as an established root cause. There is no automatic retention scheduler. Canonical SQLite is authoritative; Chroma indexes are derived and rebuilt after restore. See MANUAL_EVIDENCE.md for context/budget and approval-version semantics.
