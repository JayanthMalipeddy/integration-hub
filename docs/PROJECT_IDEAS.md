# Project selection

Scores are engineering judgments on a 1–5 scale, not market research. Weights: business value 25%, portfolio 20%, solo feasibility 20%, independence from paid services 20%, differentiation 15%.

| Idea | Business | Portfolio | Solo | Free operation | Differentiation | Weighted /5 |
|---|---:|---:|---:|---:|---:|---:|
| Integration Hub | 5 | 5 | 4 | 5 | 4 | 4.65 |
| API Architect Studio | 4 | 5 | 4 | 5 | 3 | 4.25 |
| UAE Services Navigator | 5 | 4 | 3 | 3 | 3 | 3.70 |
| Meeting-to-Execution | 4 | 4 | 5 | 4 | 2 | 3.90 |
| API Security/Governance Review | 5 | 5 | 3 | 5 | 3 | 4.30 |
| Finance Reconciliation Investigator | 5 | 4 | 3 | 5 | 4 | 4.25 |
| Developer Incident Handoff | 4 | 4 | 5 | 5 | 2 | 4.10 |
| Evidence-Based Deal Review | 4 | 5 | 4 | 5 | 3 | 4.25 |

## 1. Integration Hub — selected

Problem/users: support engineers manually correlate gateway logs, connector errors and runbooks. Example: determine whether recurring 401s reflect expired tokens, then propose safe checks. Agents: tool-selection planner and RCA analyst, supported by deterministic triage/verifier and approval coordinator. Integrations: log exports, knowledge files, Ollama; optional Nebius/Pinecone/Mem0/Langfuse. Credits fund comparative inference, retrieval and tracing experiments; free substitutes are Ollama/Chroma/SQLite. Complexity medium; feasible for one developer with a bounded incident taxonomy. Monetization hypothesis: team support workspace subscription or deployment/support services. Differentiation: evidence traceability, approved recovery planning and portable state. MVP: four error families with durable approval; expansion: read-only gateway/observability connectors, dependency maps and organization-specific runbooks.

## 2. API Architect Studio

Problem/users: integration architects repeatedly translate requirements into specs and tests. Example: generate a proposed customer API from a mapping specification. Agents: requirements analyst, spec designer, contract reviewer. APIs: OpenAPI parser, GitHub draft artifacts. Credits: Nebius for design, Langfuse for traces, Pinecone for standards. Free: local model, local spec validators, Chroma/SQLite traces. Complexity medium; solo feasible if restricted to REST. Monetization hypothesis: design-review workspaces. Differentiation: deterministic validation against company standards. MVP: a reviewed spec and test cases; expansion: mapping code, SOAP bridges and governed publishing.

## 3. UAE Services Navigator

Problem/users: business applicants reconcile documents across services. Example: prepare a checklist with official sources and dates. Agents: requirements extractor, official-source retriever, uncertainty reviewer. APIs: official public web pages; web search. Credits: Keenable/Nebius/Pinecone. Free: operator-curated official exports, local model and index; live freshness still needs internet. Complexity high due to regulatory freshness and multilingual evaluation. Solo feasible with one narrowly scoped service. Monetization hypothesis: business onboarding workflow support. Differentiation: source and effective-date tracking. MVP: one service checklist with human review; expansion: more jurisdictions and languages. Not selected because unverified official information creates a larger accuracy burden.

## 4. Meeting-to-Execution

Problem/users: project leads manually turn notes into tasks. Example: extract owners and unresolved decisions from a transcript. Agents: decision extractor, task planner, reviewer. APIs: Granola exports and optional task system. Credits: Granola/Nebius/Mem0. Free: user-supplied transcript, Ollama and SQLite; optional locally installed transcription. Complexity low-medium, strong solo feasibility. Monetization hypothesis: private team meeting workflows. Differentiation: proposed task evidence and approval before task creation. MVP: import text and approve local tasks; expansion: calendar/task connectors and transcription.

## 5. API Security and Governance Review

Problem/users: API teams miss inconsistent authentication/rate-limit policies. Example: flag an unauthenticated administrative operation. Agents: spec inspector, policy retriever, remediation reviewer. APIs: OpenAPI specs and read-only gateway policy exports. Credits: Nebius/Pinecone/Langfuse. Free: local model, schema checks, local retrieval and traces. Complexity medium-high; solo feasible on a small policy set. Monetization hypothesis: governance review tooling. Differentiation: rule-backed findings and evidence. MVP: five rules plus approved remediation report; expansion: CI checks. Security conclusions need specialist validation.

## 6. Finance Reconciliation Investigator

Problem/users: finance operations teams investigate unmatched transactions. Example: correlate a payment timeout with a posted ledger entry without replaying the payment. Agents: discrepancy triage, evidence retrieval, resolution planner. APIs: CSV ledgers and read-only payment exports. Credits: Nebius/Mem0/Langfuse. Free: deterministic Python reconciliation, Ollama and SQLite. Complexity high due to sensitive data and accounting semantics. Solo feasible for synthetic CSVs. Monetization hypothesis: reconciliation investigation assistance. Differentiation: deterministic amounts and approval boundaries. MVP: local discrepancy report; expansion: regulated connectors and audited case management.

## 7. Developer Incident Handoff

Problem/users: rotating support teams lose investigation context. Example: produce a handover with timeline, attempted checks and unresolved questions. Agents: timeline extractor, memory retriever, handoff reviewer. APIs: incident exports and optional ticket reads. Credits: Granola/Mem0/Nebius. Free: imported notes, SQLite and local inference. Complexity low-medium, high solo feasibility. Monetization hypothesis: team incident memory. Differentiation: links from every claim back to the incident record. MVP: reviewed handoff; expansion: shift schedules and ticket connectors. Less differentiation than the selected investigation workflow.

## 8. Evidence-Based Deal Review

Problem/users: procurement teams repeatedly compare agreements to policy. Example: extract payment terms and flag a clause that conflicts with policy. Agents: extraction, compliance review and risk summarization. APIs: document import and local policy corpus. Credits: Nebius/Pinecone/Langfuse. Free: local document parsing, Ollama, Chroma and SQLite. Complexity medium; solo feasible with a narrow document type. Monetization hypothesis: procurement review assistance. Differentiation: clause-level evidence and reviewer approval. MVP: one policy pack; expansion: version comparison and approved ticket creation. This overlaps Week 2 more than the selected project.

The selected project has the strongest fit with the builder's webMethods, MuleSoft, API gateway and production-support experience. It demonstrates genuine multi-step decision-making while remaining useful entirely offline once models and dependencies are installed.
