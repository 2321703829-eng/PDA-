# 2026-04-18 menu action client action mapping draft added

## What Changed

- Expanded [四类主单统一页面结构规范草稿](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/00_四类主单统一页面结构规范草稿.md) with a draft mapping for:
  - menu naming
  - `ir.actions.act_window` naming
  - execution-page client action naming
  - XML ID prefix organization
  - the relationship between list entry, detail entry, and execution entry

## Why

- The spec had already covered page structure, Odoo component mapping, execution-page landing, and module/file ownership.
- The next useful implementation-oriented step was to standardize entry-object naming so future menu/action wiring does not drift across modules.
- This is especially important because warehouse pages need to stay aligned with the logistics module’s structural rhythm while still keeping WMS-specific execution pages in `logistics_wms_web`.

## Current Decision

- Menus should stay user-facing and business-readable in Chinese.
- XML IDs should stay concise, English, and object-oriented.
- Normal document entry should prefer `act_window`.
- Execution pages should prefer client actions with a stable, action-oriented naming scheme.
- Menu, action, view, and client action identifiers should reuse a unified `logistics_wms` prefix family.
