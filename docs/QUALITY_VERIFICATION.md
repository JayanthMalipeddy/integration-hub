# Integration Hub quality verification

Measured run: eval-5d6d1cdb82ba at 2026-10-24T14:06:16.031095+00:00

15/18 task checks passed (83.33%). Simulated approval completion: 12/12 eligible cases (100.0%).

## Implemented changes

- Eleven readable frontend pages, shared components, API client and state hook; Prettier formatting enforced in CI.
- Up to two analyst corrections with persisted validation feedback, bounded graph execution and unchanged human approval requirements.
- Nomic document/query task prefixes, sentence-aware chunks and versioned collection identities.
- Broader secret redaction and normalized injection screening, including checks on retrieved evidence. These are best-effort checks, not a complete injection defense.
- Project-owned Chroma service at http://127.0.0.1:8082; data in runtime/chroma-server.
- Active model stage, elapsed time and analysis attempt visibility; benchmark history and configuration details in the dashboard.
- Eighteen synthetic cases with baseline/holdout breakdowns, explicit expected-document citation checks and isolated simulated approval completion.

## Verification

- 63 Python tests passed, including correction exhaustion, malformed responses, canonical-source rejection, model outage/restart, credential redaction and approval safety.
- Frontend production build, lint and formatting checks passed.
- Browser check: all 11 views rendered; sample form and theme controls passed; no JavaScript exceptions.
- Real local Chroma retrieval returned the expected authentication runbook.
- Dashboard API metrics exactly match the completed JSON benchmark artifact.
- Interactive workspace at final check: 8 runs and 2 tickets; benchmark tickets and memory remain in isolated evaluation storage.

## Measured outcomes

| Group | Passed | Total | Percent |
|---|---:|---:|---:|
| All task checks | 15 | 18 | 83.33% |
| Baseline task checks | 5 | 6 | 83.33% |
| Holdout task checks | 10 | 12 | 83.33% |
| Simulated completion | 12 | 12 | 100.0% |

Failed cases: missing-evidence, holdout-no-logs, holdout-healthy.

| Retrieval | Mean latency (ms) | Correct top-1 | Measurements |
|---|---:|---:|---:|
| lexical | 0.356 | 36 | 36 |
| vector | 204.139 | 36 | 36 |

Vector timing includes embedding and HTTP latency. The four-runbook workload does not establish a general retrieval-speed ranking.

## Evidence and limits

- Raw result: ../evaluations/results/eval-5d6d1cdb82ba.json
- The interrupted run eval-79ccb92dae64 is retained under runtime/evaluations with its outage note and partial results. It did not publish an aggregate score.
- The older 5/6 (83.33%) benchmark remains historical evidence. The new task rubric also requires the expected tool and a citation to the expected document, so scores are not a controlled before/after comparison.
- Holdout cases are newly authored synthetic scenarios, frozen before evaluation; they are not independent production incidents. One model run per case does not establish reliability across repeated runs.
- Exact quotation checks do not prove semantic support. Completion uses a simulated operator; actual incident resolution and human-rated usefulness are not measured.
- Cloud services remain disabled and live-unverified. The application remains single-user with one investigation admitted per backend process.
- Video recording and GitHub publication were excluded from this work.

No academy grade is claimed. The original evaluation report remains the review of the earlier implementation.


## Remaining planner limitation

All three failed task checks ultimately reached the expected safe human handoff. They failed because the planner chose a retrieval tool instead of the expected request_human decision. This is a tool-selection and unnecessary-work limitation, not an unauthorized ticket write. The bounded correction limit was exercised on unsupported findings.

| Case | Actual tool | Expected tool | Final state | Analysis attempts |
|---|---|---|---|---:|
| missing-evidence | search_runbooks | request_human | needs_human | 1 |
| holdout-no-logs | search_memory | request_human | needs_human | 3 |
| holdout-healthy | search_runbooks | request_human | needs_human | 2 |

Additional browser checks passed for benchmark-history selection and rendering a malformed response as a human handoff. These checks used a browser-only fixture and did not alter backend records.

Approved hypotheses accumulate inside the isolated benchmark run. Cases are executed sequentially rather than with an empty memory reset for every case; these are stateful workflow measurements.
