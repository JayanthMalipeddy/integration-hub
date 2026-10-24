# Integration Hub quality verification

Measured run: eval-8881397d2059 at 2026-10-24T17:31:48.051201+00:00.

18/18 task checks passed (100.0%). Simulated approval completion: 12/12 eligible cases (100.0%).

## Implemented changes

- Evidence-aware planning: vague complaints and successful health checks without linked failures request human investigation. Search queries are only required for retrieval.
- Blank logs can skip the model; titles suggesting previous incidents still reach the planner. Unknown error categories do not automatically block retrieval.
- Human-handoff messages explain the missing evidence. Existing source validation, bounded analyst correction and approval requirements remain in force.
- Eleven frontend pages with shared controls, an API client and a state hook.
- Nomic task prefixes, sentence-aware chunks and a project-owned Chroma service on port 8082.
- Persistent SQLite checkpoints, canonical source checks, best-effort redaction and injection screening.
- Actual planner decisions are saved with benchmark rows for inspection in the dashboard.

## Verification

- 73 Python tests passed, including nine planner routing regressions and the existing correction, approval, security and provider tests.
- Separate planner boundary checks: 10/10 passed, using nine real local-model calls and one deterministic blank-log shortcut. These checks measure tool choice, not retrieval quality or complete investigations.
- The active backend was restarted with the updated planner. API and frontend-proxy dashboard responses exactly match the complete latest benchmark artifact.
- Current workflow and evaluation code hashes match the measured artifacts; the 18-case dataset is unchanged from the previous benchmark.
- Earlier frontend build, lint, formatting and eleven-view browser checks remain historical verification. This update changes no frontend source.
- Evaluation checkpoints, tickets and memory stay in isolated storage. The dashboard receives the completed report only.

## Measured outcomes

| Group | Passed | Total | Percent |
|---|---:|---:|---:|
| All task checks | 18 | 18 | 100.0% |
| Baseline task checks | 6 | 6 | 100.0% |
| Original holdout split (now regression cases) | 12 | 12 | 100.0% |
| Simulated completion | 12 | 12 | 100.0% |

Failed task checks: none in this run.

## Planner comparison

The previous run scored 15/18 (83.33%). Its three planner failures eventually reached a safe handoff, after unnecessary retrieval and analysis. The table compares those same inputs with the new run.

| Case | Previous time (s) | New time (s) | New tool | Analyst calls | Task check |
|---|---:|---:|---|---:|---|
| missing-evidence | 110.15 | 17.32 | request_human | 0 | Passed |
| holdout-no-logs | 323.40 | 14.82 | request_human | 0 | Passed |
| holdout-healthy | 200.47 | 16.51 | request_human | 0 | Passed |

These are individual observed timings, not repeated controlled performance trials. Nonblank inputs still require a model decision. The blank-input shortcut does not imply millisecond latency for all insufficient-evidence cases.

## Retrieval measurements

| Retrieval | Mean latency (ms) | Correct top-1 | Measurements |
|---|---:|---:|---:|
| lexical | 0.334 | 36 | 36 |
| vector | 175.946 | 36 | 36 |

Vector timing includes embedding and HTTP latency. The four-runbook workload does not establish a general retrieval-speed ranking.

## Evidence and limits

- [Latest workflow result](../evaluations/results/eval-8881397d2059.json).
- [Planner boundary checks](../evaluations/results/planner-779ddf407eb6.json).
- [Previous 18-case result](../evaluations/results/eval-5d6d1cdb82ba.json) and the original six-case result remain unchanged.
- The baseline/holdout labels are preserved for historical comparison. The twelve original holdout cases have now informed changes and are development regression cases, not independent unseen validation. New independent cases and repeated runs are still needed.
- All data is synthetic. One local run per case does not establish production accuracy or reliability. Planner boundary cases were authored for this change and do not contribute to the 18-case score.
- Unknown failures may be investigated by retrieval, but the existing four-category evidence validator can still require human review. Tool selection alone does not establish diagnostic correctness.
- Exact quotes do not prove semantic support. Completion uses simulated approval; real incident resolution and human-rated usefulness are not measured.
- Approved hypotheses accumulate within each isolated benchmark run. Cases run sequentially rather than resetting memory between cases.
- Cloud services remain disabled and live-unverified. The application remains single-user with one investigation admitted per backend process.
- An initial benchmark attempt, eval-1259f67587a6, was stopped during development review before the final handoff wording. Its local partial evidence is retained and no aggregate score was published.

No academy grade or general accuracy score is claimed.
