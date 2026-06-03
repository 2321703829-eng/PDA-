# 2026-04-21 phase4 docs synced for frontend entry and dynamic required fields

## Summary

Updated the phase4 design docs again to lock the latest product-level positioning of template entry points and the dynamic required-field rule between order snapshots and goods base data.

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## What Changed

- Clarified that the single flat-sheet import is the frontend’s main entry
- Clarified that the existing three-sheet structure is only a phase4 transitional contract and may be hidden from frontend users
- Clarified the role split:
  - `order_line` stores snapshot-style order information and display-facing goods snapshots
  - `goods_line` stores relatively stable goods base information and remains the factual source
- Added the “master-data first, snapshot fallback” dynamic required-field rule
- Clarified that first-round image evidence still only attaches to `customer_line`, not yet to `order_line`

## Why

The latest discussion moved the design from a pure structural split toward a clearer product contract: frontend should stay simple, internal layering should stay robust, and repeated fields between order snapshots and goods base data should be validated by source priority instead of rigidly forced in every case.
