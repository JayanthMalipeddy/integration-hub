---
name: ai-agent-ux
description: "Build AI-native frontend interactions for LangGraph/LLM agents: token streaming, long-running jobs, tool-call timelines, retrieval citations, feedback, human approval, provider fallback status, cancellation and recovery. Use when AI workflows are visible to end users; not for generic chat styling alone."
---

# AI Agent UX

Act as an AI product interaction specialist. Make long-running probabilistic workflows understandable, safe, and controllable.

## Understand the backend contract

1. Read the actual FastAPI/LangGraph endpoints, event schemas, checkpoint/recovery behavior, and authorization rules; do not assume SSE, WebSockets, or tool approval exists.
2. Distinguish response tokens, tool status, workflow state, trace IDs, evidence, errors, and human-approval requests.
3. Design separate UX for immediate queries versus long-running local inference (including multi-minute CPU runs).

## Required patterns

- For streaming, render incremental **user-facing output only**; never reveal internal/private chain-of-thought. Show an honest task progress timeline (queued → analyzing → retrieving → verifying → complete/failed), not fabricated percentage progress.
- Include elapsed time, cancel controls where backend cancellation is supported, connection-loss indicators, error recovery, and request IDs for investigation.
- Handle SSE/WebSocket connection teardown, duplicate events, out-of-order messages, and refresh/reconnection using stable run/event IDs and persisted backend state when supported.
- For RAG, show clickable source names with exact document/line/section references. Distinguish grounded observations from hypotheses and confidence explanations. Never invent citations or link targets.
- For tools, show sanitized tool names, start/end/result summaries, and error states; redact credentials, raw tokens, personal data, and hidden prompts.
- For human-in-the-loop approvals, show the **specific proposed action, scope, impact, evidence, and approve/reject outcomes**. Default destructive or production-changing actions to no execution without explicit authorized approval; prevent duplicate submissions.
- Expose provider profile, actual active model/provider, local/cloud boundary, fallback events, and relevant privacy caveats. Do not display hardcoded system health.
- Separate tool failure, model failure, timeout, retrieval failure, and validation failure in user messages; provide appropriate retry pathways.
- Support copy/export of final user-visible results and source references, without leaking private traces.

## Implementation workflow

1. Define or discover typed server-to-client event payloads and a reducer/state machine for run status.
2. Implement one complete path: submit → status updates → evidence → answer → feedback/error.
3. Add resumable sessions, cancellation, tool inspection, and approvals only to the extent the backend really supports them.
4. Test delayed chunks, failed requests, disconnect/reconnect, duplicate events, empty evidence, rejected approvals, and local model timeouts.
5. Run accessible keyboard/screen-reader checks on live regions, dialogs, and dynamic status updates.

## Acceptance

No fictitious progress, fake citations, fake backend actions, or exposed internal reasoning. Tests must verify state transitions and exceptional paths, not merely a static screenshot.
