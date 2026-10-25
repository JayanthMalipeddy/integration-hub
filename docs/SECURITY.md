# Security boundaries

This is a local single-user application, not a production-certified security product.

Implemented controls:

- Local-only listening ports in native startup; Compose publishes only the frontend on loopback.
- Required bearer API token by default, same-origin restrictions and trusted host middleware. Startup fails closed without a token; REQUIRE_AUTH=false is an explicit development/test override.
- Fixed server-side tenant identity; keyed storage/collections prevent client-provided tenant impersonation. Tests exercise cross-tenant memory isolation.
- Typed incident/document inputs; actual streamed request bodies bounded to 100 KB even without Content-Length. Uploaded TXT/MD/JSON only, UTF-8 and maximum 50 KB.
- Redaction of common credentials, email/identity patterns, labeled names/phones and international phone numbers. Filtering covers titles, structured records, model boundaries, storage, traces and exports. This is not exhaustive DLP.
- Common instruction-injection patterns trigger a handoff/rejected upload. Retrieved text is screened before analysis and labeled untrusted in prompts. Unicode compatibility normalization and zero-width character removal improve common-pattern screening. Pattern matching cannot detect every injection; authorization remains deterministic.
- Model-selected tools are schema-enumerated and read-only. No arbitrary shell, unrestricted URL fetch or executable recovery text exists.
- Durable approval before the local ticket/memory write; decline and replay behavior tested.
- Bounded provider retries, timeouts, circuit breakers, maximum graph steps and token budgets. One active run per API process and six start requests per minute.
- Cloud data transfer and paid calls disabled by default. Persisted conservative spending reservations and explicit external-export commands.
- Credentials are not embedded in frontend builds or returned by configuration endpoints. The entered access token lives in browser-tab memory only; cloud exceptions do not echo provider response bodies.
- Backup path validation, checksum verification and refusal to overwrite existing restore targets.

Known limits and deployment requirements:

- Use one backend process. Admission locks and rate limits are process-local; the spending ledger is not a distributed multi-worker quota system. Reserve costs assume operator-configured correct rates; account-side hard caps are still required.
- API request bodies and file reads are bounded; the supplied Nginx adds a second size limit and content security policy. Container header behavior still needs runtime verification.
- Add organizational SSO/RBAC, HTTPS, encrypted volumes/backups, retention/deletion policy, audit export and proper multi-tenant identity before public/team exposure.
- Common-pattern redaction is not proof that confidential data has been removed. Use synthetic data for this demo; organization-approved handling is needed for real office logs.
- Citation integrity and category consistency are necessary checks, not semantic truth. Human review remains required. No claims of zero hallucination or perfect root-cause accuracy are made.
- Stored memory is explicitly a reviewed hypothesis. Approving a ticket is not evidence that a repair succeeded.
- Optional cloud speech, search, memory sync and trace export are contract-tested only and disabled unless configured and authorized. No production systems are modified.

Authenticated readiness and operational metrics are exposed at /api/ready and /api/operations. The Provider configuration page shows process-local counts and alerts. See [security verification](SECURITY_VERIFICATION.md) for evidence and limitations.

Historical storage is not automatically rewritten: read-time redaction does not erase older database pages or backups. Backup ZIP files are not encrypted by the application; laptop disk encryption was not assessed.
