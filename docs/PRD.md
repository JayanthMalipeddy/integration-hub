# Product requirements and acceptance

**One-liner:** My agent helps integration support engineers investigate API failures in a browser workspace, replacing manual log/runbook correlation. It parses logs and chooses between two read-only tools, drafts a cited recovery plan, and hands off whenever evidence is missing or before creating a recovery ticket. Success is a reviewable, evidence-backed investigation with zero unapproved writes; time is measured per run.

## Scope

- Users: one local support engineer, with a future team deployment path.
- Input: sanitized log excerpts and UTF-8 runbooks/API specifications/meeting exports.
- Output: categorized hypothesis, exact source quotes, uncertainty, checks, proposed recovery, trace and optional approved local ticket.
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
| Evaluation evidence | 6 real synthetic cases, 83.33% task pass rate; raw cases retained |
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
