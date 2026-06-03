# 2026-04-18 inbound button state matrix added

## What Changed

- Expanded [入库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/02_入库管理/00_入库单状态机草稿.md) with a dedicated inbound button-to-state linkage section.
- Added:
  - the phase-1 inbound button scope
  - a state/button matrix across the seven main states
  - button-specific interpretation for submit, cancel, start receipt, start putaway, and terminated
  - a suggested button layering model for the detail page
  - a set of phase-1 anti-patterns to avoid

## Why

- The inbound topic file had already stabilized the main state machine and exception-handling boundaries.
- The next useful step was to connect those states to visible document actions so later detail-page design and implementation can align with the state model.
- This provides a cleaner bridge between state-machine design and page-action design.

## Current Decision

- `draft` primarily carries submit/cancel actions.
- `waiting_receipt / receipting` carry receipt-related actions.
- `received / putawaying` carry putaway-related actions.
- `done / cancel` are viewing/tracing oriented.
- `terminated` remains a restricted dangerous action under `receipting`, not a normal peer action to the main warehouse flow.
