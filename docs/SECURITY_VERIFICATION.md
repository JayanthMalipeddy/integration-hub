> Current update (25 October 2026): [targeted gap repairs and verification](GAP_REPAIR_VERIFICATION.md) and [manual evidence contract](MANUAL_EVIDENCE.md) supersede the older behavior/counts below where indicated. Historical measurements remain preserved.

# Security and operational verification

## Scope

This update strengthens the existing local, single-user application. It does not introduce organizational login, user roles or a distributed deployment. All security fixtures use synthetic data.

## Authentication

The API requires a configured bearer credential by default and refuses startup when REQUIRE_AUTH is true without API_TOKEN. Data routes, diagnostics, OpenAPI and API documentation require authentication. Local-only binding and browser origin/host restrictions remain in place.

Run `python -m scripts.configure_access` once before starting the backend. It generates a random token in the ignored project-local .env file without printing it. The combined startup script runs this setup automatically. Enter API_TOKEN in the browser connection screen. The browser keeps it only in memory for that tab; Disconnect clears access. Reloading the page requires reconnecting.

REQUIRE_AUTH=false is an explicit development/test escape hatch, not a production configuration. The current running instance has authentication enabled. Environment variables override .env values, so inherited empty or outdated settings must be corrected before startup.

## Privacy boundaries

Redaction now covers labeled customer/full/patient names, labeled phone numbers and international phone patterns, in addition to the earlier credential, email and identity rules. Structured private fields are redacted recursively.

Document titles and bodies, incident fields, model request data, parsed findings, model-call metadata, stored records and traces, API exports, and checkpoint views pass through privacy filtering. Ingestion IDs are derived from the sanitized title and body.

Legacy database records are sanitized when read. This does not rewrite old database pages, checkpoints, backups or model-service logs. New workflow inputs and parsed outputs are sanitized before checkpointing. No claim is made that historical sensitive content has been erased.

Redaction remains pattern-based. Unlabeled names, unusual identifiers, encoded content and context-dependent confidential information can remain. These controls are not exhaustive data-loss prevention or a basis for uploading real office data without organizational approval.

## Guardrails and request handling

Injection screening includes incident metadata, document titles and retrieved evidence. Additional checks cover explicit instructions to forward sensitive incident/customer content to external destinations. The fixed read-only tool set, evidence validator, bounded reflection and human approval gate remain the final action boundaries.

Actual request bodies are limited to 100 KB, including streamed requests with no Content-Length or a misleading length. Malformed and duplicate lengths are rejected. File uploads retain their separate 50 KB limit. API responses include no-store, nosniff, frame-denial and referrer headers. The container reverse proxy also defines a content security policy.

## Operations

The authenticated /api/ready endpoint checks canonical database access, model availability, embeddings and the vector store. It returns 503 when required dependencies are unavailable. /api/health is a separate liveness endpoint.

The authenticated /api/operations endpoint records request counts by status and a p95 over the latest 200 request durations. Counters are process-local and reset on restart. It stores no request bodies, credentials or raw URLs.

The Provider configuration page displays these measurements and alerts for rejected authentication, server/readiness failures and saved failed investigations. These are in-application notices, not external paging. Failed-run counts cover saved history, not only new failures.

API request timing excludes background inference; workflow traces remain the source for model latency. The limit remains one active investigation per backend process and six start attempts per minute. Admission limits and spending reservations are not distributed quotas.

## Verification results

- 110 Python tests passed in 6.33 seconds, including 37 new authentication, privacy, request-limit, readiness and adversarial cases.
- Frontend TypeScript/Vite build, lint and formatting checks passed.
- Eight headless-browser checks passed: protected initial screen, invalid credential rejection, valid connection, no credential in web storage, operational panel, benchmark history, disconnect, and a 390px viewport. No JavaScript exceptions were observed.
- Live API and frontend proxy reject unauthenticated dashboard requests with 401 and accept the configured token. Authenticated readiness returned 200 with all four checks passing.
- Docker Compose configuration validated with mandatory authentication settings. Docker's engine was unavailable; container build, container startup and container security headers are not runtime-verified.

## Measured workflow regression

The new real local run passed 18/18 workflow checks and 12/12 simulated approval completions. The separate planner suite passed 10/10 cases. Its nine model calls and one blank-log shortcut are not included in the workflow score.

Workflow evidence: [eval-0ebc2478b3a7.json](../evaluations/results/eval-0ebc2478b3a7.json). Planner evidence: [planner-63ae4c53ef28.json](../evaluations/results/planner-63ae4c53ef28.json). The current source hash and both authenticated dashboard responses match the full workflow artifact.

These are synthetic regression measurements on known cases, not independent accuracy estimates, a penetration test, a security certification or proof of production readiness. Earlier artifacts remain unchanged.

## Remaining production work

Organizational identity and permissions, document-level access policy, HTTPS termination, managed encryption and secret rotation, retention and deletion across all derived stores, independent red teaming, alert delivery and incident ownership, container runtime verification, and disaster-recovery exercises remain necessary for broader deployment.

Distributed workers, shared quotas, inference load balancing, application-level retrieval/answer caching and concurrency/load tests should be introduced when moving beyond this single-user scope. No MCP integration is present, so MCP-specific security has not been implemented or assessed.
