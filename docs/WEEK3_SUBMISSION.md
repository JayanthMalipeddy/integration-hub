# Integration Hub: project notes

## Why I chose this project

I built Integration Hub around a problem familiar from integration support: working out why an API failed and finding the evidence needed to act on it. My experience with webMethods, MuleSoft, API gateways and messaging shaped the use case.

The workspace brings logs, runbooks and investigation history together. The agent selects a tool, checks source quotations and proposes a recovery plan. Creating a local ticket requires human approval, and the investigation can resume after a restart.

## Data and implementation

The corpus contains four synthetic runbooks covering expired credentials, partner rate limits, upstream timeouts and JDBC pool exhaustion. The current evaluation includes six baseline cases and twelve newly authored holdout cases, including missing evidence and malicious instructions embedded in logs. No customer or office data is included.

I used the Week 3 handout and the vendor-independent platform prompt to define the scope. Runtime prompts in `backend/app/workflow.py` guide tool selection and evidence-based analysis. Ollama runs the local models, Chroma indexes the runbooks, and SQLite stores canonical records and checkpoints. Cloud adapters are optional; their live behavior has not been verified.

## What changed during development

- Added persistent checkpoints and an approval pause before local writes.
- Checked quotations against stored sources instead of treating valid JSON as proof of a grounded answer.
- Added a bounded reflection loop so the agent can retry an analysis using validation feedback. A real replay of the partner-quota citation failure passed after one correction.
- Connected the eleven workspace views to stored records and measured evaluation results.
- Split the frontend into pages, components and hooks to make it easier to maintain.
- Fixed a Windows backup issue by explicitly closing SQLite connections.

## Results and lessons

The latest saved benchmark passed 15 of 18 task checks (83.33%). All 12 eligible cases completed simulated approval successfully. Three cases failed the planner-choice checks and ended in a human handoff. The full results and limitations are in [quality verification](QUALITY_VERIFICATION.md).

My main lesson was that a well-formed answer can still lack the evidence needed to support it. Validation and correction need to be part of the workflow. Human approval also needs to survive restarts and remain tied to the exact proposed action.

Lexical retrieval was faster than vector retrieval on this small corpus, with equal top-1 results. That is a useful local measurement, but it does not establish which method will work best on a larger dataset. More independent cases and human-reviewed findings are needed before making broader accuracy claims.
