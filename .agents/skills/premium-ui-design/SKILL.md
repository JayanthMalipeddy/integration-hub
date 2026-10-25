---
name: premium-ui-design
description: "Design or redesign polished enterprise SaaS/AI application screens, layouts, and user journeys. Use when asked to improve visual quality, usability, responsive hierarchy, navigation, empty states, or the premium feel of an existing frontend. Do not use for code architecture-only refactors."
---

# Premium UI/UX Design

Act as a senior product designer who can ship implementation-quality frontend code. Prioritize information hierarchy, real workflows, accessibility, and product coherence—not decorative effects.

## Discover the product

1. Inspect existing pages, actual domain terminology, target users, API capabilities, and current theme; map the user's primary tasks and decision points.
2. Identify problem areas: confused navigation, information overload, illegible density, weak error states, unclear calls to action, missing evidence/context.
3. Establish one visual direction aligned with the product (enterprise observability, developer console, administrative operations, etc.). Use references for quality standards, not logo/color cloning.

## Design quality standards

- Define a consistent typography scale, spacing rhythm, radii, border hierarchy, light/dark palettes, and semantic state colors via the design system.
- Prefer clear grid alignment, generous but purposeful space, readable widths, strong page titles, meaningful summaries, and progressive disclosure for technical detail.
- For dashboards, distinguish status, evidence, risks, and recommended actions; put user-critical information above decorative visualization.
- Provide polished, functional loading, empty, success, warning, error, offline, and permission-denied states. Skeletons must match layout shapes and avoid layout shift.
- Design for desktop and small screens; prevent horizontal overflow and manage dense tables through priority columns, responsive details, or controlled scrolling.
- Use restrained motion for transitions and feedback; honor reduced-motion preference. Do not make animations essential to understanding.
- Maintain WCAG 2.2 AA targets for keyboard access, focus visibility, contrast, labels, and touch targets where applicable.
- Never invent metrics or integrations to fill dashboard space. Label sample/demo data clearly.

## Execute

1. Propose screen hierarchy and interaction states before touching multiple files.
2. Reuse existing design-system primitives; add variants/tokens only when genuinely needed.
3. Implement one representative screen end to end, including its real behavior, then apply the system consistently.
4. Validate real content extremes: empty data, long technical strings, multiple languages, many cards, large timestamps, and error responses.
5. Compare mobile/tablet/desktop screenshots when tools permit; check keyboard and reduced-motion usability.

## Completion criteria

- Every advertised action either works or is explicitly labeled unavailable.
- The UI improves task completion, clarity, and consistency—not just appearance.
- Report changed screens, design decisions, verified interactions, and any unavailable browser checks.
