# 2026-04-18 inbound search filter groupby rules added

## What Changed

- Expanded [入库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/02_入库管理/00_入库单状态机草稿.md) with a dedicated section for:
  - inbound search-field baseline
  - inbound filter baseline
  - inbound group-by baseline
  - the layered relationship between `state`, `exception_state`, and `terminated_reason`
  - the distinction between normal list usage and exception-focused views

## Why

- The inbound topic file had already stabilized state semantics, display language, field storage, navigation rules, and stock-object linkage.
- The next useful step was to make list/search behavior explicit so later search views and list analysis can align with the same state model.
- This helps prevent state and exception logic from being mixed into one ambiguous filter layer.

## Current Decision

- Search should primarily focus on fast locating fields such as document number, owner, and warehouse.
- Filters should primarily focus on main state, supplementary exception state, and time windows.
- Group-by should primarily focus on main state, supplementary exception state, owner, warehouse, and date.
- `state`, `exception_state`, and `terminated_reason` should continue to be treated as three separate analytical layers.
