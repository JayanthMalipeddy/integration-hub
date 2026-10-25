# Interface redesign and verification

Verified locally on 25 October 2026 in `C:\Projects\integration-hub`. ReguGraph was not changed. No dependencies, software, model weights, or fonts were installed for this revision.

## What changed

- Graphite/teal design system, consistent typography, surfaces and controls; matching light theme.
- Task-grouped navigation, useful page descriptions, mobile menu and a skip link. Placeholder initials and unconditional green health indication were removed.
- Overview prioritizes measured metrics, pending reviews and recent investigations. The workflow diagram is explanatory, not live telemetry.
- Investigation search/status filtering, semantic keyboard-operable links and explicit no-match states.
- Citation titles where provided by the retrieved evidence, with original source IDs and quotations retained. Benchmark metadata and raw evidence remain available through disclosures.
- Native approval/deletion dialog with action context, Cancel as the initial focus, explicit Tab containment, Escape cancellation, and focus restoration. Duplicate action submissions are guarded.
- API sync status, last successful sync time, stale-data retention, non-overlapping polling and cancellation of superseded reads. Polling pauses in hidden tabs.
- Thirty-second API request deadlines; uncertain write timeouts do not trigger automatic retries. Background sync does not erase action errors.
- Explicit connection, empty, no-match, loading and failure states; render-error recovery boundary.
- Shared contrast and focus styling, readable long values, responsive provider tables and reduced-motion support.

Implementation uses existing React, TypeScript, Vite, CSS and Lucide dependencies. No framework migration or API contract change was needed.

## Executed checks

| Check | Actual result |
| --- | --- |
| `python -B -m pytest tests -q -p no:cacheprovider` | 110 passed in 7.25 seconds |
| `npm test` in frontend | 9 API-client tests passed |
| `npm run build` in frontend | TypeScript and production build passed; Vite build 1.18 seconds |
| `npm run lint` in frontend | Passed |
| `npm run format:check` in frontend | Passed |
| `python -B scripts/verify_enterprise_ui.py` | 94 browser assertions passed, zero JavaScript exceptions |
| `python -B scripts/rollback_enterprise_ui.py` | Archive integrity, current target hashes and in-memory restoration rehearsal passed; 20 frontend files in restore set |

Build output: JavaScript 272.03 kB / 83.97 kB gzip; CSS 28.48 kB / 6.84 kB gzip. This is bundle size, not a load-test or Core Web Vitals score.

The browser matrix covers 11 pages at 1440x1000, 768x1024 and 390x844 in dark and light themes: 66 render/overflow checks. The remaining assertions cover authentication, credential storage, search, filtering, keyboard navigation, dialog focus/cancellation, evidence expansion, offline recovery, empty states, long titles, reduced motion, mobile controls and disconnect. Repeated Tab steps are individual assertions, not separate end-to-end scenarios.

Form submission, duplicate approval prevention and action-failure persistence are tested with browser-only response fixtures. No real approval, memory deletion, document upload or model job was sent by the browser test. The backend suite provides separate API/workflow regression coverage. Browser checks require running local services, configured API_TOKEN, saved benchmarks and at least one pending investigation; they are not part of hosted CI.

The existing GitHub Actions frontend step now includes `npm test`. Hosted CI has not run for these local changes.

[Raw browser results](UI_BROWSER_VERIFICATION.json) include every assertion. Screenshots are in `docs/screenshots/enterprise-*.png`; working captures are in `runtime/ui-verification`. Existing historical screenshots were used for initial design comparison; they are not an exact automated before/after pixel baseline.

## Visual and accessibility review

Inspected rendered desktop dark/light overview, mobile overview, analytics and approval dialog. The browser matrix checks layout boundaries; it is not a full visual-diff engine.

Measured token contrast ratios: dark main text 15.41:1, dark muted text 7.75:1, light main text 15.46:1, light muted text 6.07:1. Primary button labels: dark 9.29:1 and light 5.79:1. Input border against background: dark 3.46:1 and light 3.14:1. These sampled token checks and keyboard tests do not establish full WCAG conformance. Screen-reader testing and other browser engines were not performed.

## Rollback

The exact pre-redesign frontend, including pre-existing uncommitted security/UI changes, is archived locally at:

`runtime/ui-rollback/20261025-082431/frontend-before.zip`

SHA-256 manifests identify original and completed files. The rollback tool restricts its targets to the frontend, verifies archive integrity and refuses to overwrite frontend files edited after this revision. It preserves backend files, application data, secrets and unrelated project changes. A rescue archive of affected current files is created before restoration.

From the project root, inspect readiness without restoring:

```powershell
.\.venv\Scripts\python.exe -B scripts/rollback_enterprise_ui.py
```

To restore the previous UI when requested:

```powershell
.\.venv\Scripts\python.exe -B scripts/rollback_enterprise_ui.py --restore
npm.cmd run build --prefix frontend
```

The restore command has not been executed against the active frontend; its effect was rehearsed in memory. The new UI remains active. Rollback archives stay local under ignored runtime storage.

## Production-readiness boundary

This is a verified local interface and frontend reliability improvement, not certification of the complete system for enterprise deployment. Existing platform constraints still apply:

- Shared API-token access is not organization-integrated SSO/RBAC or demonstrated tenant isolation.
- The current process supports one active investigation. Distributed workers, failover and high-concurrency load handling remain unverified.
- Public TLS, container runtime, operational alert delivery and backup restoration need validation in the target environment. Existing Compose/Nginx preparation does not prove a live deployment.
- Browser coverage is installed Microsoft Edge; other browsers, assistive technologies and real mobile hardware remain unverified.
- Some existing backend response types still use the broad Item type; complete runtime response-schema validation is not claimed.
- No paid/cloud integration was exercised. The model benchmark was not rerun for this frontend change; the dashboard still displays the existing saved 18/18 synthetic result with its provenance.

See [deployment](DEPLOYMENT.md) and [security verification](SECURITY_VERIFICATION.md) for the remaining platform work. No deployment, commit or remote push was performed in this revision.
