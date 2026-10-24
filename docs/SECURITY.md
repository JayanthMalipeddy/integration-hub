# Security boundaries

This is a local single-user application, not a production-certified security product.

Implemented controls:

- Local-only listening ports in native startup; Compose publishes only the frontend on loopback.
- Optional bearer API token, same-origin write restrictions and trusted host middleware.
- Fixed server-side tenant identity; keyed storage/collections prevent client-provided tenant impersonation. Tests exercise cross-tenant memory isolation.
- Typed, length-limited incident/document inputs; uploaded TXT/MD/JSON only, UTF-8 and maximum 50 KB.
- Redaction of common password/token, Basic/Bearer authorization, database URI credentials, private-key blocks, AWS access-key IDs, email and identity patterns before canonical ingestion. This is not exhaustive DLP.
- Common instruction-injection patterns trigger a handoff/rejected upload. Retrieved text is screened before analysis and labeled untrusted in prompts. Unicode compatibility normalization and zero-width character removal improve common-pattern screening. Pattern matching cannot detect every injection; authorization remains deterministic.
- Model-selected tools are schema-enumerated and read-only. No arbitrary shell, unrestricted URL fetch or executable recovery text exists.
- Durable approval before the local ticket/memory write; decline and replay behavior tested.
- Bounded provider retries, timeouts, circuit breakers, maximum graph steps and token budgets. One active run per API process and six start requests per minute.
- Cloud data transfer and paid calls disabled by default. Persisted conservative spending reservations and explicit external-export commands.
- No secrets in frontend, checked-in files, traces or reports by design; cloud exceptions do not echo provider response bodies.
- Backup path validation, checksum verification and refusal to overwrite existing restore targets.

Known limits and deployment requirements:

- Use one backend process. Admission locks and rate limits are process-local; the spending ledger is not a distributed multi-worker quota system. Reserve costs assume operator-configured correct rates; account-side hard caps are still required.
- Request Content-Length is checked and file reads are bounded. A production reverse proxy must also bound streamed/chunked body sizes; the supplied Nginx does so.
- Add organizational SSO/RBAC, HTTPS, encrypted volumes/backups, retention/deletion policy, audit export and proper multi-tenant identity before public/team exposure.
- Common-pattern redaction is not proof that confidential data has been removed. Use synthetic data for this demo; organization-approved handling is needed for real office logs.
- Citation integrity and category consistency are necessary checks, not semantic truth. Human review remains required. No claims of zero hallucination or perfect root-cause accuracy are made.
- Stored memory is explicitly a reviewed hypothesis. Approving a ticket is not evidence that a repair succeeded.
- Optional cloud speech, search, memory sync and trace export are contract-tested only and disabled unless configured and authorized. No production systems are modified.
