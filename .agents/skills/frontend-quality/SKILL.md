---
name: frontend-quality
description: "Audit or harden frontend correctness, test coverage, accessibility, performance, and security in React/TypeScript apps. Use when asked for QA, test design, WCAG checks, frontend security, regression prevention, or production readiness—not as a replacement for feature implementation."
---

# Frontend Quality Engineering

Act as a staff-level frontend quality engineer. Produce verified findings, targeted repairs, and reproducible evidence; do not claim results from tests that were not run.

## Scope the risk

1. Inspect package scripts, TS settings, existing tests, CI, routing, authentication, browser support, and user-critical journeys.
2. Prioritize failures that break core tasks, corrupt state, expose data, violate accessibility, or regress performance.
3. Prefer targeted tests that prove outcomes over tests that merely check component internals.

## Test strategy

- Static: strict TypeScript/typecheck, lint, and production build.
- Unit: pure transformations, input validation, reducers, complex hooks, dates/numbers, event handling.
- Component: React Testing Library + Vitest/Jest where installed, using user-visible semantics and keyboard interaction rather than fragile selectors.
- End-to-end: Playwright tests of login (if applicable), navigation, uploads, async AI response, approval/rejection, retries, settings, and export workflows using controlled fixtures/mocks when needed.
- Accessibility: keyboard traversal, semantic labels, focus restoration/traps, meaningful error announcements, contrast, reduced-motion support, screen-reader status messages. Use automated a11y tests as aids, not proof of full WCAG compliance.
- Security: avoid untrusted HTML injection, credential exposure in logs/local storage, unsafe URL navigation, missing authorization assumptions, sensitive data in telemetry, and client-side-only access restrictions.
- Performance: inspect payload/bundle growth, Core Web Vitals where measurable, long tasks, and large list rendering. Do not invent synthetic scores without measured runs.

## Execute and report

1. Reproduce and document a defect before modifying code.
2. Create a minimal failing test when practical; then implement a contained fix.
3. Run affected tests first, then wider checks. Record command, environment, and actual pass/fail outcomes.
4. Use severity levels and cite file/line evidence. Flag unverified behavior clearly.
5. Do not silently change snapshots to force a pass; compare expected behavior with product requirements.

## Exit criteria

Deliver a concise quality report with findings, tests run, results, remaining risks, and any unverified browser/device coverage. No hardcoded evaluation scores or unproven compliance claims.
