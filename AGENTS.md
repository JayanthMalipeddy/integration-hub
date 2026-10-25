# Project-wide instructions for Codex

## Mission
Ship enterprise-quality frontend changes that are **functional, accessible, responsive, fast, maintainable, and verifiable**. Apply the repository's existing stack and conventions before introducing new ones.

## Working rules
1. Inspect `package.json`, the lockfile, routes, API contracts, state layers, tests, and project-specific instructions before edits.
2. Preserve existing UI behavior and backend contracts unless the user explicitly requests changes. Prefer incremental, reversible work over broad rewrites.
3. Do not compress large features into one TSX file. Keep bootstrapping small; separate pages, features, components, hooks, clients, types, and pure utilities by responsibility.
4. Default to strict TypeScript and semantic HTML. Avoid `any` and unsupported assumptions about API responses.
5. Favor existing UI libraries and design tokens; do not add dependencies without justification.
6. Every displayed control must work, be disabled with an explanation, or be explicitly identified as a demo. No invented telemetry, evaluation results, citations, provider health, or progress percentages.
7. Build complete loading, empty, error, offline/timeout, and success states. Handle API cancellation/cleanup for long-running agent requests.
8. Never expose secrets, sensitive logs, internal model reasoning, or destructive tool actions without explicit approval and server-side authorization.
9. Verify changed paths with available typecheck, lint, unit tests, and build. When changing visuals, use actual browser screenshots/interactive checks where available.
10. Clearly distinguish tests actually run from work not verified. State real blockers instead of claiming success.

## Specialist skills
Invoke the most relevant skill, not all skills automatically:
- `frontend-architecture`: structure, boundaries, monolithic component refactors.
- `premium-ui-design`: high-quality screen redesigns and UX flows.
- `design-system`: shared visual tokens, themes, accessible primitives.
- `ai-agent-ux`: streaming, citations, agent status, human approvals.
- `dashboard-engineering`: data-rich charts, tables, monitoring screens.
- `frontend-quality`: tests, accessibility, security, performance audit.
- `visual-qa`: browser screenshots and visual regression checks.

## Delivery format
Provide a short change summary, relevant files, tests/commands and actual results, and outstanding risks. For audits, give evidence-backed findings with priority and affected code locations.
