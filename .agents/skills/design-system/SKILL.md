---
name: design-system
description: "Create, extend, or rationalize a React design system: tokens, colors, typography, spacing, Tailwind theme, shadcn/ui or Radix primitives, shared component APIs, and dark/light modes. Use when consistent theming or reusable UI components are the core task; not for page-specific product flows."
---

# Design System Engineering

Act as a design-system engineer. Establish consistency through reusable, accessible primitives with small, stable APIs.

## Audit

1. Inspect CSS/Tailwind versions and configuration (Tailwind v3 and v4 differ), installed UI libraries, and existing tokens before changing setup.
2. Inventory repeated patterns (button, input, dialog, tab, badge, table, toast, sheet) and inconsistent colors, spacing, focus rings, and state conventions.
3. Avoid replacing an existing component library without a clear, requested migration rationale.

## Token and component design

- Create semantic tokens (`background`, `foreground`, `surface`, `muted`, `border`, `primary`, `destructive`, `success`, `warning`, `info`, focus ring) rather than page-specific colors.
- Ensure coherent dark/light themes, sufficient contrast, and consistent data-series palettes. Avoid relying on color alone to indicate status.
- Use well-defined typography, spacing, radius, shadow, and motion scales; limit one-off values.
- Wrap Radix/shadcn primitives in application patterns only when there is repeated real use. Keep keyboard behavior, focus traps, portal behavior, labels, and aria relationships intact.
- Type component props; preserve refs where necessary; support disabled, busy, validation, danger, and selected states where relevant.
- Keep styles scoped and predictable. Use variant helpers already in the project; avoid parallel competing styling systems.
- Document usage for nonobvious components and show representative states. Adopt Storybook only if justified by project size/needs.

## Workflow

1. Define the current components and gaps in a compact inventory.
2. Implement or normalize tokens and a few high-leverage shared primitives.
3. Migrate affected views incrementally, avoiding unrelated visual changes.
4. Check dark/light rendering, semantic contrast, keyboard behavior, small-screen spacing, and long text.
5. Run typecheck, lint, tests, and build; update snapshots deliberately after visual review.

## Quality gate

Every new component must have a clear purpose, typed API, state behavior, theme support where applicable, and at least a lightweight test or documented manual verification. Do not introduce a separate library or dependency merely for visual polish.
