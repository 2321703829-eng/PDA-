# 2026-04-18 outbound button state matrix added

## What Changed

- Expanded [出库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/04_出库管理/00_出库单状态机草稿.md) with a dedicated outbound button-to-state linkage section.
- Added:
  - the phase-1 outbound button scope
  - a state/button matrix across the eight main states
  - button-specific interpretation for submit, cancel, pick, check, ship, and terminated
  - a suggested button-layering model for the detail page
  - a set of phase-1 anti-patterns to avoid

## Why

- The outbound topic file had already stabilized the main state machine and exception boundaries.
- The next useful step was to connect those states to visible document actions so later detail-page design and implementation can align with the same state model.
- This gives outbound the same state-to-action clarity already established for inbound.

## Current Decision

- `draft` primarily carries submit/cancel actions.
- `waiting_pick / picking` carry pick-related actions.
- `picked / checking` carry check-related actions.
- `waiting_ship` carries shipping entry actions.
- `done / cancel` are viewing/tracing oriented.
- `terminated` remains a restricted dangerous action under `picking / checking`, not a normal peer action to the main warehouse flow.
