# Selected development prompts and iterations

These are actual requests from the project conversation, selected to explain the development process. They are not reconstructed claims about an unavailable initial build history. Private operational identifiers are omitted.

| Actual request | Implementation decision | Verification / learning |
|---|---|---|
| "Add Intra-Graph Reflection ... so Case 2 self-corrects its citation omission autonomously" | Bounded verify-to-analyze repair edge; explicit citation feedback | Existing Case 2 regression verifies a missing runbook citation is corrected inside the graph. Prompt repair does not establish causal truth. |
| "analyze what you provide, distinguish facts from hypotheses, and request specific missing details instead of assuming access or inventing a cause" | Versioned manual evidence, source-line observations, targeted questions and explicit unavailable answers | Same-run follow-up and stale-review rejection tested. No production database access is required. |
| "when i click on download selected report button, word document need to be downloaded instead of md file" | In-memory DOCX export using the existing Python environment | Authenticated export and redaction tests; evidence/questions added without replacing the download flow. |
| "work only on the gaps, dont touch the ones which are working fine and doest need rework" | Targeted modules and a local rollback snapshot; preserve layout, provider adapters and shared Chroma topology | Full backend/frontend suites and browser navigation/action checks; old benchmark artifacts preserved. |

Tools used in this iteration: Codex for source inspection and targeted edits; pytest for backend regressions; existing TypeScript/Vite/oxlint/Prettier and Node tests; installed Edge for browser checks; existing Ollama and shared Chroma for recorded live evaluations. No software was installed during the gap-repair iteration.

A useful lesson was that exact quotations can accompany a wrong explanation. The accepted evidence summary now uses quoted observations, while unverified causal prose cannot silently become a recovery ticket. Diagnostic usefulness still needs independent operational review.

Another lesson was that a local passing test suite is not a published submission. The final repository snapshot, required document and recorded demonstration must refer to the same reviewed release. The implementation does not invent a recording or a trainer grade.
