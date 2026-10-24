# Week 3 submission notes

## Project overview

Integration Hub helps integration support engineers investigate API failures through a browser workspace. The builder's experience with webMethods, MuleSoft, API gateways, messaging and production support shaped the selected use case. Unlike a one-turn RAG answer, it chooses a tool, maintains shared state, validates evidence, pauses for human approval and resumes with an auditable local write.

## Dataset and prompts

Four synthetic runbooks cover expired credentials, partner rate limits, upstream timeouts and JDBC pool exhaustion. Six synthetic cases add insufficient evidence and a malicious instruction embedded in a log. No office/customer data is included in the demo corpus. The full dataset is in `data/`.

Coding instructions: the Week 3 handout and user-supplied vendor-independent platform prompt. Implementation reasoning: local-first operation, concrete agent decisions, canonical storage and strict distinction between mocked tests and actual benchmark outcomes. Runtime prompts are in `backend/app/workflow.py`: planner tool selection and evidence-constrained analyst synthesis, both with structured schemas and an untrusted-input instruction.

## Iterations and observations

1. Started with a separate project folder and ports to preserve the completed Week 2 build.
2. Verified the installed Ollama models and made a real Qwen call before relying on the architecture.
3. Implemented a bounded graph with persistent checkpoints and a real interrupt before local writes.
4. Added source-quote and canonical-record checks. The actual model sometimes omitted required evidence despite a schema-valid answer; that failure is visible and safely handed off.
5. Built eleven connected workspace screens and fed evaluations from stored measurements rather than fixed scores.
6. Added cloud adapter contracts and explicit export commands, keeping live cloud integrations disabled without consent/keys.
7. A Windows backup test revealed that sqlite context managers do not close connections; explicit closing fixed the file-lock failure.

Learning: schema validity is not grounding; a quote can exist while the answer lacks a required source. Approval must be persistent and tied to the exact state. Local-first portability requires canonical records outside vendor indexes. On this tiny corpus, inexpensive lexical matching was much faster than embedding-based retrieval with equal top-1 results; that does not establish a general ranking.

## Live demo plan — under five minutes

- 0:00–0:35: Explain the user/problem and show the Overview. State that the data is synthetic.
- 0:35–1:00: Start the authentication incident and show the agent's available read-only tools.
- 1:00–2:00: While inference runs, show knowledge documents, provider status and the workflow trace. Explain local inference latency honestly.
- 2:00–3:10: Open a completed investigation if the live run is still processing. Show hypothesis, uncertainty, source quotations and the approval pause.
- 3:10–3:45: Approve the local ticket; show the new ticket/memory. Explain that no external service was restarted.
- 3:45–4:15: Submit the injected-log scenario and show immediate human handoff.
- 4:15–4:50: Show 83.33% task outcome, the failed rate-limit citation case, real retrieval timings and cloud profiles marked not run.

This is a demo outline for submission preparation, not a completed video. The handout also requires a shared Google Doc, a <=5-minute recording and a GitHub link. Those external deliverables have not been published or submitted automatically. No final submission form was sent.
