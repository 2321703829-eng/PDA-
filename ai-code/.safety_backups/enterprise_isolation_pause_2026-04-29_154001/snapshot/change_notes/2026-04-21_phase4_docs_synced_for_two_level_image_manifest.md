# 2026-04-21 phase4 docs synced for two-level image manifest

## Summary

- synced phase4 docs with a two-level image package manifest design
- clarified that a waybill image package contains multiple store image packages
- clarified that the business minimum image attachment unit remains `customer_line`

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## Key Decisions

- image packaging is layered as `waybill package -> store package -> image files`
- the waybill package manifest describes store subpackages, not image details
- the store package manifest directly describes image files and scene metadata
- first-round image attachment still recognizes only `customer_line`
