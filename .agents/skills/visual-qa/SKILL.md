---
name: visual-qa
description: "Verify real rendered frontend screens with browser screenshots and visual regression checks across desktop, tablet, mobile, dark/light modes, and UI states. Use for UI verification after design/refactor changes or pixel/layout bugs; do not invoke when no visual behavior is involved."
---

# Visual QA

Act as a meticulous frontend visual reviewer. Use actual rendered evidence when a browser or screenshot tool is available. Never present imagined screenshots as observations.

## Establish baseline

1. Identify local startup commands, routes, authentication/demo data, and viewport targets from the repository.
2. If browser automation exists, launch the app and inspect key screens. If inaccessible, clearly state the blocker and perform code-only layout review without claiming screenshot validation.
3. Save before/after images with consistent viewport, zoom, theme, data, and interaction state. Avoid comparing mismatched dynamic timestamps or randomized content.

## Essential test matrix

- Desktop (e.g. 1440×900), tablet (768×1024), mobile (390×844); adjust to product audience.
- Light and dark theme where supported.
- Default, long-content, empty, loading, validation-error, network-error, dialog/menu open, selected/expanded, and focused states.
- Navigation shell, dashboard, document upload, AI result/citations, agent timeline, settings, tables, and charts as relevant.

## What to inspect

- Horizontal overflow, hidden controls, clipped labels, overlapping panels, and inconsistent padding.
- Typography scale, hierarchy, line length, contrast, density, and touch-target reachability.
- Sticky headers/sidebar behavior, responsive tables, modals, dropdown stacking, and scroll trapping.
- Keyboard-visible focus, tab sequence, dialogs, and content updates without layout shift.
- Streaming states and very long AI output including code, JSON, paths, URLs, and citation markers.
- Actual interaction: click/keyboard controls, upload, search, filter, sort, expand, retry, and navigation; do not infer function from appearance.

## Work and reporting

1. Reproduce one visual issue with a route, viewport, state, and screenshot or clear repro steps.
2. Fix the smallest relevant layout/style cause, avoiding unrelated redesign.
3. Re-capture and compare the same state; review any screenshot diffs manually before updating baselines.
4. Run typecheck/tests/build after changes. Identify blockers to browser-based verification.
5. Summarize tested states and viewports, concrete defects corrected, screenshots saved, and remaining visual risks.

## Standard

Never state 'pixel perfect' without inspecting real render output. A successful build is not proof of visual correctness.
