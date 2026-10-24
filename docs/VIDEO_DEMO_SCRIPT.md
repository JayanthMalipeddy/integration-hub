# Integration Hub
## Video demonstration script

Target duration: 4 minutes 45 seconds; stay below the handout's five-minute limit. Read only the narration paragraphs aloud. Actions and checks are presenter instructions. This script uses one transparently pre-run investigation, followed by live approval and a live guardrail example, to avoid hiding local inference latency.

## Before recording — preparation only

1. Open http://127.0.0.1:5180 and confirm the backend and Ollama are running. Check Provider configuration: local_free and the required local models should be ready.
2. In Agent workspace, select Customer API authentication failure. Click Start investigation before recording. It can take roughly 2–3 minutes on this laptop.
3. Wait until it reaches awaiting_approval. Note its run ID. Leave it unapproved so the video can demonstrate the real approval. If it needs human review, show that honestly and use another evidence-valid awaiting-approval run; do not describe a failed run as successful.
4. Confirm no investigation is actively running. The API allows only one active run. Review Reports & exports and Memory and note existing items; do not imply that existing data is empty.
5. Check Analytics & evaluations. The saved baseline is 83.33% (5/6); if you rerun evaluations, read the values actually displayed rather than repeating old numbers.
6. Keep the architecture diagram available in a second tab or Word window. Use synthetic logs and close unrelated office information. Use an already approved recording tool; this script requires no new software installation.

## 0:00–0:25 — Pleasant introduction and problem

SHOW: Overview. Keep the project name and measured task result visible.

SAY: Hi everyone, I'm Jayanth. Today I'd like to show you Integration Hub, my Week 3 agentic AI project. It helps integration support engineers move from API error logs to an evidence-based investigation and a reviewable recovery plan. The focus is useful automation, while keeping the engineer in control.

DO: Point briefly to the investigation cards and the awaiting-review count. Do not read every dashboard card.

## 0:25–0:50 — Incident input and honest timing

SHOW: Agent workspace, then RCA investigation.

DO: Click the Customer API authentication failure sample to show the title, service and logs. Do not start a second run. Switch to RCA investigation and select the awaiting-approval run prepared earlier.

SAY: Here is a synthetic customer API failure returning a 401 error. I ran this investigation shortly before recording because local inference can take a few minutes. We can now inspect the actual result and complete the approval live. The agent selects an allowed read-only tool instead of simply answering the log as a chatbot.

## 0:50–1:15 — Architecture and agent roles

SHOW: docs/diagrams/system_architecture.svg, or the architecture page in the technical specification.

SAY: The interface uses React and TypeScript, with FastAPI behind it. LangGraph coordinates the investigation and saves checkpoints in SQLite. Ollama runs Qwen locally, while local embeddings and Chroma retrieve runbook passages. A planner chooses the tool, an analyst drafts the hypothesis, and deterministic checks enforce evidence and approval rules.

DO: Follow browser → API → workflow → provider boundary. Point to the approval gate and local records. Return to the application.

## 1:15–1:45 — Retrieval and evidence

SHOW: Knowledge library briefly, then RCA investigation for the selected run.

DO: Expand the authentication runbook. Return to the investigation, show Evidence trail and expand Retrieved context.

SAY: These are the reference runbooks. The selected passages stay attached to the investigation with source identifiers. Here we can compare the quoted log evidence with the relevant runbook text. The system checks that quotations exist and match the retained sources. That establishes evidence integrity, but it does not prove every conclusion is correct.

## 1:45–2:10 — Hypothesis, uncertainty and trace

SHOW: RCA investigation, then Execution timeline for the same run.

DO: Point to Root-cause hypothesis, What remains uncertain and Recommended checks. In the timeline, expand the planner or tools event and show the actual provider/model and latency.

SAY: The output is deliberately presented as a hypothesis, with recommended checks and unresolved uncertainty. The execution timeline shows which tool was chosen and what each stage produced. Provider, model and timing details come from the real run. If evidence is insufficient, the workflow hands the investigation back to a person.

## 2:10–2:45 — Live human approval

SHOW: RCA investigation → approval panel → Reports & exports → Memory.

DO: Return to the prepared awaiting-approval run. Review its evidence, enter a short note, click Review and approve, then Confirm. Wait for completed status. Find the new ticket by run/title under Reports & exports, then show its reviewed hypothesis under Memory.

SAY: The workflow has paused before creating a recovery ticket. After reviewing the evidence, I can approve or decline. I'll approve this synthetic example now. The system creates a local planned ticket and retains the reviewed hypothesis. It does not restart an external service, and the memory is not labeled as a proven root cause.

CHECK: Show an actual new ticket, not an unrelated existing one. If the UI reports a conflict or error, use the contingency notes below rather than claiming approval succeeded.

## 2:45–3:15 — Live guardrail demonstration

SHOW: Agent workspace → Suspicious instruction inside a log entry → RCA investigation.

DO: Confirm the previous operation has finished. Select the suspicious-instruction sample and click Start investigation. Wait for needs_human, then show its Execution timeline.

SAY: Next, this synthetic log contains an instruction asking the system to ignore its rules. Logs are treated as data, not instructions. This guardrail detects the pattern and sends the case for human investigation before a model call. Pattern checks are not a complete security guarantee; the restricted tool permissions provide another boundary.

CHECK: The trace should show triage and handoff, not successful planner/analyst calls for this run.

## 3:15–3:55 — Actual evaluation and retrieval performance

SHOW: Analytics & evaluations. Scroll from metrics to Case-level evidence and Measured retrieval comparison.

DO: Highlight the task metric, expand partner-quota and show the failure. Then show both retrieval timings. Use displayed values if a newer benchmark exists.

SAY: The real local benchmark passed five of six tasks, or 83.33 percent. One rate-limit answer missed a required runbook citation, so it was handed off instead of being accepted. On four small retrieval examples, lexical matching averaged about 0.27 milliseconds, compared with about 144 milliseconds for vector retrieval including embeddings. Both found the expected first result. This is a small synthetic comparison, not a claim that one method is always better.

## 3:55–4:20 — Portability and deliverables

SHOW: Provider configuration, then Reports & exports.

DO: Show local_free and disabled cloud consent. Select an investigation and click Download selected report if time allows.

SAY: The free local path needs no cloud key. Provider selection is centralized, so the core workflow can use other adapters without rewriting its agent logic. The cloud adapters have contract tests, but I have not presented them as live-verified integrations. Canonical documents, checkpoints and memory remain portable, and the investigation can be exported for review.

## 4:20–4:45 — Learning and close

SHOW: Overview; finish on the project name and actual benchmark card.

SAY: I used AI coding assistance to develop the application, then checked it with tests and real model runs. My main learning was that a valid JSON response is not the same as a supported answer. Reliable agent workflows need evidence checks, persistent state, failure handling and explicit approval. The next step is broader, independently reviewed incident data. Thank you for watching.

## Contingency notes — do not read unless needed

- Slow normal inference: use the prepared run and disclose it as scripted. Do not call it an instant response. For a fully fresh normal run, record separately and label any waiting-time cut honestly.
- Approval conflict or busy response: check whether another run is active. Wait for completion; if time is short, demonstrate the saved approval trace and explain that it is a previously executed result. Never claim a new ticket was created unless it is visible.
- Prepared run already approved: create a new synthetic run before recording. A completed run cannot be approved again.
- Guardrail request cannot start: show the stored injected-log case and explicitly call it a recorded result. Do not describe a replayed screen as a new live execution.
- No evaluation loaded: verify the saved evaluation is present before filming. Never replace missing results with manually entered percentages.
- Over five minutes: omit the report download and shorten the architecture explanation; retain evidence review, approval, guardrails and the failed benchmark case.
- Optional decline take: prepare a separate awaiting-approval run, choose Decline ticket and show declined status. No new ticket or memory should be created for that run. This is optional and outside the main 4:45 script.

## Final recording checklist

- Project name and business problem are clear.
- Pre-run normal investigation is disclosed, with real local inference latency acknowledged.
- Tool selection, retrieved evidence and uncertainty are visible.
- Approval result and guardrail behavior are demonstrated accurately.
- The failed benchmark case remains visible; no unsupported 100% accuracy claim.
- Cloud/production limitations are stated briefly.
- Recording is under five minutes and contains no credentials or office/customer data.
