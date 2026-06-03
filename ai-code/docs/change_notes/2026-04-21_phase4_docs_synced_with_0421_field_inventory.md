# 2026-04-21 phase4 docs synced with 0421 field inventory

## Summary

Synced phase4 design docs with the latest field inventory workbook:

- `ai-code/数据库底表，更新日期4.21.xlsx`

The new sync focuses on:

1. Treating the 4.21 workbook as the current authoritative field pool.
2. Reconfirming the phase4 structure as:
   - `waybill`
   - `order_line`
   - `goods_line`
3. Reclassifying latest fields into:
   - waybill snapshot fields
   - order snapshot fields
   - goods factual fields
4. Introducing `运单分组号` as the new system-side import grouping key when external `运单号` is absent.
5. Updating order-key priority to match the latest workbook:
   - `单据号/单据编号`
   - `销售订单号`
   - `源单单号`
   - `第三方单号`

## Updated docs

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期导入模板字段级映射与校验规则清单.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期单表字段逐字段全量映射表.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期后端数据库与接口影响面调研稿.md`

## Key design changes

- Added a system-control field zone to the redesigned single-sheet import template.
- Added `运单分组号` as the recommended hard-required key for waybill aggregation.
- Promoted the 4.21 workbook fields as the concrete basis for redesigning database bottom tables and the single import sheet.
