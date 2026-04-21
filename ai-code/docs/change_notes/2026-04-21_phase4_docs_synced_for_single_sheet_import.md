# 2026-04-21 phase4 docs synced for single-sheet import

## Summary

Updated the phase4 design docs to reflect the newly agreed import direction:

- user-facing import can provide one combined flat sheet
- internal system structure still stays on the three-layer standard model

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## What Changed

- Added the judgment that phase4 should support a user-facing single-sheet quick import mode
- Clarified that the internal standard structure remains `waybill / customer_line / goods_line`
- Added mapping-script positioning between the flat import sheet and the internal three-layer structure
- Added mapping topics such as waybill aggregation rules, customer-line aggregation rules, goods-line row rules, and conflict rules
- Synced the import topic so that single-sheet import is treated as an input simplification layer instead of an internal model flattening
- Kept the previous image-package direction and order auto-mount direction aligned with the new single-sheet import design

## Why

The latest business discussion confirmed that users would benefit from maintaining one combined spreadsheet, but the system still needs the existing layered internal model for stable order mounting, trace/evidence hanging, and later query expansion. The design docs needed to be updated so both judgments coexist without conflict.
