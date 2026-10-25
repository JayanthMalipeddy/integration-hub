---
name: dashboard-engineering
description: "Engineer data-rich React dashboards with genuine KPIs, tables, timelines, filtering, date ranges, charting, log viewers and performance-aware real-time updates. Use for analytics/observability screens and operational data exploration; not for purely decorative landing pages."
---

# Dashboard Engineering

Act as a senior dashboard engineer. Ensure that every displayed statistic has a documented source, unit, calculation, timestamp, and expected refresh behavior.

## Data contract first

1. Inspect schemas, API endpoints, data cardinality, refresh rate, and the exact meaning of metrics; clarify denominators, nulls, time zones, and status semantics.
2. Keep server state in a query/cache layer; encode filters and pagination in URL/query state where bookmarking matters.
3. Normalize data through typed adapters, not ad hoc transformations embedded in chart components.

## UI components

- Build reusable KPI tiles with label, unit, time window, comparison reference, loading/error state, and data freshness.
- Choose charts by the question: line for trends, bar for category comparisons, scatter for relationships, table for precise values. Avoid pie charts when comparisons are difficult.
- Apply meaningful axis labels and accessible tooltips; never truncate values so their units or meanings become misleading.
- Use robust tables for sorting/filtering/pagination, with virtualization where log/trace volumes justify it. Provide empty, no-match, error, and loading states distinctly.
- For incidents, implement timelines with consistent local/UTC presentation, correlated IDs, filtering by status/service/severity, and an accessible detail panel.
- Make analytics traceable back to source records rather than displaying AI-generated approximate counts as measured values.

## Performance and correctness

1. Prefer server-side pagination/filtering for large datasets; memoize expensive transformations only after profiling.
2. Debounce high-frequency search and filter inputs; cancel stale requests and guard against race conditions.
3. Avoid unnecessary rerenders and massive DOM node counts; ensure charts resize correctly and do not leak observers.
4. Prevent chart jitter when streaming or polling; show the last successful refresh timestamp.
5. Cover edge cases: zero denominators, missing dates, NaN, huge ranges, daylight saving changes, duplicate incidents, and empty datasets.

## Verification

Validate every displayed metric against fixtures or backend records; test query filters, table keyboard use, responsiveness, and charts under extreme/empty values. If sample data is used, clearly mark the UI as demonstration data.
