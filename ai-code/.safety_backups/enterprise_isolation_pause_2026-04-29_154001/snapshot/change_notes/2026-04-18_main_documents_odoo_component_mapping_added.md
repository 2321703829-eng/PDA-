# 2026-04-18 main documents Odoo component mapping added

## What Changed

- Expanded [四类主单统一页面结构规范草稿](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/00_四类主单统一页面结构规范草稿.md) with an Odoo-facing component mapping section.
- Added explicit mapping from page blocks to:
  - `ir.actions.act_window`
  - `search view`
  - `tree/list view`
  - `form view`
  - `header buttons`
  - `button_box / smart buttons`
  - `one2many tree/form`
  - custom execution-page containers in `logistics_wms_web`
  - hint bar / toast / confirm modal feedback layers
- Added a new “view vs frontend carrier” split so the team can distinguish:
  - what should stay in business-module native Odoo views
  - what should be carried by `logistics_wms_web` as unified custom interaction shells

## Why

- The page-structure spec had already become stable enough at the information-architecture level.
- The next useful step was to translate that structure into Odoo view/component language so later backend, frontend, and review work can stay aligned.
- This also reduces the risk of over-customizing ordinary list/detail pages while still reserving custom frontend capacity for execution-heavy warehouse flows.

## Current Decision

- Standard list/detail pages for the four main documents should continue to prefer native Odoo views.
- Execution pages should prefer custom containers in `logistics_wms_web`.
- Unified feedback layers such as hint bars, toast, and confirm dialogs should also be treated as web-layer capabilities rather than duplicated document by document.
