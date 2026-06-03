# 2026-04-18 inbound field dictionary and state storage added

## What Changed

- Expanded [入库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/02_入库管理/00_入库单状态机草稿.md) with a new section for:
  - inbound field dictionary baseline
  - state-field storage strategy
  - supplementary exception-state storage strategy
  - `terminated_*` field storage guidance
  - page-to-field mapping for status and exception display

## Why

- The inbound topic file had already stabilized state meanings, button linkage, execution-record linkage, display language, and navigation rules.
- The next useful step was to make the state machine more implementation-ready by clarifying how the main state and exception state should actually land on the model.
- This helps future model design avoid mixing process state, exception state, and page-only display concepts.

## Current Decision

- `state` remains the sole carrier of main inbound process states.
- `exception_state` remains the carrier of supplementary exception status.
- Phase-1 `terminated_*` fields should stay directly on the inbound main model as a lightweight exception bundle.
- Page labels and filters should read directly from these core fields rather than from parallel page-only status fields.
