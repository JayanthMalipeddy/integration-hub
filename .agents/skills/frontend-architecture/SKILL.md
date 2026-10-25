---
name: frontend-architecture
description: "Architect, refactor, or review React/TypeScript frontends for maintainability and scalability. Use for monolithic TSX files, feature/module boundaries, API integration layers, state ownership, routing, and behavior-preserving migrations. Do not invoke for visual styling-only tasks."
---

# Frontend Architecture

Act as a principal frontend architect. Optimize for correct behavior, clear module boundaries, and maintainable code rather than maximal abstraction.

## Inspect before editing

1. Identify the actual stack from `package.json`, lockfile, TypeScript settings, routes, and existing conventions. Preserve the framework (Vite/React vs. Next.js) unless migration is explicitly requested.
2. Map entry points, UI routes, cross-page state, providers, API clients, models, and tests. Identify tight coupling, cyclic dependencies, duplication, and dead code.
3. For a monolithic `main.tsx`, inventory every page, event handler, API call, type, and shared state before moving code. Establish a basic behavior baseline using tests or observed app behavior.
4. Prefer small, reversible changes; do not redesign the interface during a refactor unless requested.

## Architecture rules

- Use feature-oriented ownership when it reduces coupling: `src/features/<feature>/{components,hooks,api,types}` plus shared `src/components/ui`, `src/lib`, and `src/app` only where helpful.
- Keep `main.tsx` to application bootstrapping and providers. Route components orchestrate features; presentation components receive typed props.
- Keep transport logic in one typed API client per bounded domain. Centralize base URLs, auth handling, error normalization, and request cancellation; never scatter `fetch` calls through unrelated components.
- Use TanStack Query for server state if already adopted or justified; local component state for ephemeral UI; Zustand/Context only for genuinely cross-cutting client state. Avoid duplicating server state into global stores.
- Model async state explicitly: idle/loading/success/error, retry semantics, and cancellation. Prefer discriminated unions to boolean combinations.
- Enable strict TypeScript; avoid `any`, broad type assertions, hidden side effects, and circular imports. Validate untrusted API responses where appropriate.
- Define boundaries for streaming and long-running jobs: a typed event contract, connection lifecycle, reconnect/cancel behavior, and separate rendering from event processing.
- Preserve accessible semantics while changing component structure.

## Refactoring procedure

1. Define a proposed file tree and a source-to-destination map. Record existing route names, API contracts, keyboard behavior, and visual states.
2. Extract shared types and pure functions first; add tests around critical transformations.
3. Move API access into services/hooks, then extract components page-by-page. Preserve component keys, event behavior, and form state across changes.
4. Consolidate duplicated effects; inspect dependency arrays, stale closures, subscriptions, abort controllers, and cleanup.
5. Check code splitting at route/large-feature boundaries; avoid premature micro-componentization.
6. After each slice, run the available typecheck, lint, unit tests, and build; repair regressions before continuing.

## Deliverables and verification

- Summarize architecture decisions and modified modules with rationale.
- Demonstrate route, form, state, request, and interaction parity. For a visual-preserving refactor, capture before/after screenshots when a browser is available.
- Report exact commands executed and results. If a test/tool is unavailable, mark it **not verified**, never **passed**.
- Flag remaining technical debt instead of silently widening scope.
