# 2026-04-18 counting button state matrix added

## What Changed

- Expanded [盘点单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/05_盘点与库内作业/00_盘点单状态机草稿.md) with a dedicated counting button-to-state linkage section.
- Added:
  - the phase-1 counting button scope
  - a state/button matrix across the five main states
  - button-specific interpretation for start counting, continue counting, confirm, cancel, result viewing, and adjustment initiation
  - a suggested button-layering model for the detail page
  - a set of phase-1 anti-patterns to avoid

## Why

- The counting topic file had already stabilized the main state machine and discrepancy-handling boundaries.
- The next useful step was to connect those states to visible document actions so later detail-page design and implementation can align with the same state model.
- Counting has a different rhythm from inbound and outbound, so its button model also needed an explicit dedicated baseline.

## Current Decision

- `draft` primarily carries start/cancel actions.
- `counting` carries continuation and result-viewing actions.
- `reviewing` carries discrepancy confirmation and adjustment-related actions.
- `done / cancel` are viewing/tracing oriented.
- Phase 1 should not expand counting into a separate exception-button system.
