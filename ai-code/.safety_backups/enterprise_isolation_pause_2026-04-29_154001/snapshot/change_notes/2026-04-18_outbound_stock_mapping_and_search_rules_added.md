# 2026-04-18 outbound stock mapping and search rules added

## What Changed

- Expanded [出库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/04_出库管理/00_出库单状态机草稿.md) with two new sections:
  - outbound state to native stock-object field mapping
  - outbound search/filter/group-by rules
- Added guidance for:
  - outbound document to `stock.picking` linkage
  - outbound line to `stock.move` linkage
  - pick/check/ship-confirm records to `stock.move.line` or `stock.picking`
  - how outbound main states should rely on stock execution facts
  - how search, filters, and group-by should separate `state`, `exception_state`, and `terminated_reason`

## Why

- The outbound topic file had already stabilized state semantics, button linkage, execution-record linkage, display language, navigation rules, and field storage.
- The next useful step was to connect those rules to Odoo’s execution-layer objects and to list/search analysis behavior.
- This helps outbound design stay consistent with both Odoo stock execution and the warehouse module’s page/search language.

## Current Decision

- Outbound documents remain the business-mainline carrier.
- Native stock objects remain the execution-fact carrier.
- Main-state progression should depend on stock execution facts as much as possible.
- Search/filter/group-by should continue to keep `state`, `exception_state`, and `terminated_reason` as three separate analytical layers.
