# Integration Hub: project notes

## Why I chose this project

I built Integration Hub around a problem familiar from integration support: working out why an API failed and finding the evidence needed to act on it. My experience with webMethods, MuleSoft, API gateways and messaging shaped the use case.

The workspace brings logs, runbooks and investigation history together. The agent selects a tool, checks source quotations and proposes a recovery plan. Creating a local ticket requires human approval, and the investigation can resume after a restart.

## Data and implementation

The corpus contains six investigation guides covering expired credentials, rate limits, timeouts, connection acquisition, Oracle allocation errors and authentication workload. The latter guides include official reference URLs. The current evaluation includes six baseline cases and twelve cases from the original holdout split, now reused as regression checks, including missing evidence and malicious instructions embedded in logs, plus six operational-style regressions. No customer or office data is included.

I used the Week 3 handout and the vendor-independent platform prompt to define the scope. Runtime prompts in `backend/app/workflow.py` guide tool selection and evidence-based analysis. Ollama runs the local models, Chroma indexes the runbooks, and SQLite stores canonical records and checkpoints. Cloud adapters are optional; their live behavior has not been verified.

## What changed during development

- Added persistent checkpoints and an approval pause before local writes.
- Checked quotations against stored sources instead of treating valid JSON as proof of a grounded answer.
- Added a bounded reflection loop so the agent can retry an analysis using validation feedback. A real replay of the partner-quota citation failure passed after one correction.
- Added required local API authentication, privacy filtering across model/storage boundaries and operational diagnostics.
- Refined the planner to ask for missing evidence before searching while keeping unfamiliar failures and explicit history requests eligible for retrieval.
- Connected the eleven workspace views to stored records and measured evaluation results.
- Split the frontend into pages, components and hooks to make it easier to maintain.
- Fixed a Windows backup issue by explicitly closing SQLite connections.

## Results and lessons

The pre-repair 18-case result is historical. Current measured results, the stricter observation contract and limitations are in [gap-repair verification](GAP_REPAIR_VERIFICATION.md). Diagnostic accuracy is explicitly not measured.

My main lesson was that a well-formed answer can still lack the evidence needed to support it. Validation and correction need to be part of the workflow. Human approval also needs to survive restarts and remain tied to the exact proposed action.

Lexical retrieval was faster than vector retrieval on this small corpus, with equal top-1 results. That is a useful local measurement, but it does not establish which method will work best on a larger dataset. More independent cases and human-reviewed findings are needed before making broader accuracy claims.

Actual selected development requests and lessons: [development prompts and iterations](DEVELOPMENT_ITERATIONS.md). The accepted output separates supplied observations from unverified causes; [manual follow-up](MANUAL_EVIDENCE.md) retains evidence versions and invalidates stale approvals.
