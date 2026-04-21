# 2026-04-18 counting search filter groupby rules added

## What Changed

- Expanded [盘点单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/05_盘点与库内作业/00_盘点单状态机草稿.md) with a dedicated section for:
  - counting search-field baseline
  - counting filter baseline
  - counting group-by baseline
  - the layered relationship between `state` and `difference_result`
  - the distinction between normal list usage and discrepancy-pending views

## Why

- The counting topic file had already stabilized state semantics, button linkage, discrepancy linkage, display language, field storage, and stock-object linkage.
- The next useful step was to make list/search behavior explicit so later search views and list analysis can align with the same counting state model.
- This helps prevent counting-process state and discrepancy-result logic from being mixed into one ambiguous filter layer.

## Current Decision

- Search should primarily focus on fast locating fields such as document number, warehouse, and owner.
- Filters should primarily focus on main state, discrepancy result, and time windows.
- Group-by should primarily focus on main state, discrepancy result, warehouse, owner, and date.
- `state` and `difference_result` should continue to be treated as two separate analytical layers.
