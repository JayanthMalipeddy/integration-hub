# Integration Hub
## Project specification

Week 3 | Version 0.1.0 | Documentation baseline: 24 October 2026

Project directory: C:\Projects\integration-hub

## 1. Problem, users and objective

Integration support engineers spend time correlating gateway logs, API failures, runbooks and previous incidents before deciding what to check next. Generic chatbot answers do not necessarily preserve evidence, remember investigation state or enforce approval before an action.

Integration Hub helps support engineers inspect logs, find relevant runbooks and review a possible cause. It records the sources and unanswered questions, then asks for approval before creating a local recovery ticket.

Primary user: an integration/API support engineer working with webMethods, MuleSoft, API gateways or similar enterprise integrations. The current deployment is single-user and local. Potential team use and commercial support workflows are future opportunities, not established customer or revenue claims.

One-liner: My agent helps integration support engineers investigate API failures in a browser workspace, replacing manual log/runbook correlation with tool-directed retrieval, evidence review and an approved local recovery plan.

## 2. Goals and success measures

- Complete a multi-step task with persistent state, tool selection and human handoff.
- Keep core operation independent of promotional credits and paid services.
- Separate supported evidence from hypotheses and preserve unsuccessful cases.
- Measure task completion, retrieval, latency, usage and citation integrity from actual runs.
- Make the implementation explainable through a usable UI, reproducible code and documentation.

The initial recorded benchmark achieved 5/6 task passes (83.33%) across six synthetic cases. This is a baseline for improvement, not a target rewritten after measurement or a production accuracy guarantee. No measured unapproved ticket writes occurred in those six cases. The average case latency was 115.62 seconds, including the near-instant injection rejection.

## 3. Functional scope and acceptance

| ID | Requirement | Acceptance evidence / behavior |
|---|---|---|
| FR-01 | Start an incident investigation | Valid title/service/log input creates a run ID and visible status |
| FR-02 | Select a tool | Model produces a schema-valid allowlisted tool/query; unsupported tools fail |
| FR-03 | Retrieve knowledge | Up to three passages have source identifiers and retained text |
| FR-04 | Produce a reviewable finding | Structured category, hypothesis, uncertainty, checks and recovery draft |
| FR-05 | Validate evidence | Bad/missing required citations or changed canonical records prevent approval path |
| FR-06 | Enforce human approval | Awaiting-approval run persists; approve/decline resumes it |
| FR-07 | Prevent unapproved recovery writes | Ticket/reviewed-memory writes occur only after approval |
| FR-08 | Handle failures | Failed provider/tool call is visible and checkpoint retry is available |
| FR-09 | Support knowledge management | Import bounded UTF-8 text/Markdown/JSON and rebuild derived indexes |
| FR-10 | Retain reviewed memory | Approved hypothesis is reusable, visibly unverified and explicitly forgettable |
| FR-11 | Export investigations | Markdown report includes evidence, uncertainty, recovery and model provenance |
| FR-12 | Display actual evaluation data | Dashboard and analytics consume persisted benchmark records |
| FR-13 | Select provider profiles | Central profile mapping; cloud consent/credentials remain prerequisites |
| FR-14 | Preserve portability | Backup canonical records/checkpoints and rebuild indexes after restore |

## 4. User experience

| Screen | User purpose |
|---|---|
| Overview | Review investigation counts, waiting approvals, knowledge and measured task results |
| Agent workspace | Enter an incident, choose a synthetic example and inspect available tools |
| Knowledge library | Review/import documents and rebuild the retrieval index |
| Incident analysis | Inspect original sanitized logs and parsed signals |
| RCA investigation | Review hypothesis, citations, uncertainty and approve/decline a local ticket |
| Execution timeline | Inspect actual node events, decisions, provider/model and timings |
| Analytics & evaluations | Compare measured metrics, failed cases and retrieval timing |
| Provider configuration | View profile, actual local model availability and consent/budget settings |
| Memory | Review or forget retained approved hypotheses |
| Reports & exports | Export a selected investigation and inspect approved recovery tickets |
| Settings | Enter a session API token and change appearance |

## 5. Representative user journey

1. The engineer selects the synthetic Customer API authentication failure scenario.
2. The system parses 401/invalid_token evidence and the planner selects runbook retrieval.
3. Local embeddings and Chroma return relevant passages. The analyst proposes a hypothesis and checks.
4. The verifier checks quotations, required evidence and canonical records.
5. The engineer reviews the uncertain elements and approves or declines the proposed local ticket.
6. Approval creates a planned ticket and a reviewed hypothesis. No external service is changed.
7. The engineer exports the report or inspects the trace for review and learning.

Alternative paths: suspected instruction injection hands off before model inference; insufficient evidence hands off; provider/tool failure is saved for retry; decline finishes without ticket or memory. Exact model responses are not guaranteed on every rerun.

## 6. Data and evaluation design

The demo corpus contains four authored synthetic runbooks: authentication, rate limiting, upstream timeout and JDBC connection pool exhaustion. The original six synthetic cases cover these four normal paths, missing telemetry and an instruction embedded in a log. Twelve additional synthetic holdout cases add incident wording variations, missing evidence and adversarial inputs. No production incident data is included in the supplied corpus.

The evaluation harness records case outputs, expected category/tool/status, retrieved sources, citation checks, latency, reported token counts, provider/model, dataset hash and timestamp. It stores JSON artifacts and the same result in SQLite for dashboard display. Fixture tests are never treated as actual model benchmarks.

Recorded local results: 83.33% task pass rate; category match 4/4; expected tool 4/5; retrieval hit@3 4/4; returned quote integrity 9/9. The rate-limit answer omitted a runbook citation, so its task failed even though the returned log quotes were real. Semantic correctness, production RCA accuracy and hallucination rate were not measured.

Lexical token overlap averaged 0.267 ms; vector retrieval including query embedding averaged 143.776 ms. Both returned the expected top result on four queries. This small, sequential comparison does not establish that lexical retrieval is always better.

## 7. Nonfunctional requirements and constraints

- Local usability: no cloud keys or paid inference needed after installation/model download.
- Recoverability: durable interrupts/checkpoints and a tested backup/restore path.
- Transparency: visible provenance, evidence, errors, uncertainty and measured failures.
- Bounded execution: one active investigation, defined tool set, step/token limits and bounded retries.
- Maintainability: modular backend, typed API schemas, central provider boundary and separate frontend.
- Data handling: synthetic demonstration data, common-pattern redaction, no secrets committed.
- Accessibility: labeled controls, keyboard-capable controls, responsive layout and light/dark themes; no formal accessibility certification claimed.

No formal production SLA, concurrent-team capacity, operator-time saving or cloud cost guarantee has been established. Local inference latency depends on available hardware and model load.

## 8. Deliverables and status

| Deliverable | Current status |
|---|---|
| Local application and eleven screens | Implemented; prior build/API/visual checks passed |
| Real local agent workflow | Executed with Ollama/Qwen |
| Durable approval and failure tests | Included in 30-passing-test baseline |
| Evaluation dataset, harness and raw output | Included; 5/6 task baseline retained |
| Optional cloud adapters | Implemented with mocked contracts; live verification pending |
| Technical specification and architecture diagram | Included in Markdown and Word |
| Project specification | This document, supplied in Markdown and Word |
| Setup, deployment, security and migration documentation | Included and linked from README |

## 9. Boundaries, risks and next iteration

Not implemented: production remediation, local voice/transcription, organization-wide SSO/RBAC or a public production deployment. Meeting support imports existing text/JSON exports only. Sponsored/hybrid live benchmark scores remain unavailable. Docker runtime was not validated because its engine was stopped.

Next priorities are independently authored held-out incidents, human-labeled findings, semantic claim checks, better evidence completeness, repeated retrieval experiments and organization-specific runbooks. Then validate approved cloud providers, deployment infrastructure and security controls before any wider rollout. Preserve current failure evidence when improving prompts or models.

## 10. Week 3 handout alignment

The project demonstrates agent decisions, multiple steps, read-only tools, persistent shared state, durable human approval and failure handling. Its local write is a concrete task outcome rather than a one-turn answer. Code, prompts, data, iterations and observations are documented.


## Current quality verification

15/18 task checks passed (83.33%). Simulated approval completion: 12/12 eligible cases (100.0%).

The current suite has 63 passing tests. Frontend build, lint and formatting checks passed. All eleven views passed browser navigation checks. The benchmark uses six baseline cases and twelve newly authored holdout cases, isolated storage and simulated approvals. Model-correction feedback survives backend restarts. The dashboard reads the same saved results. Earlier figures in this document are historical baseline measurements. See QUALITY_VERIFICATION.md for the complete evidence and limitations.
