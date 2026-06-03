# 2026-04-21 phase4 four design docs added

## Summary

- added four phase4 design docs for single-sheet import, field mapping, image field validation, and image frontend interaction
- aligned document placement with phase3 structure: topic spec, interface/data specs, and interaction/component spec
- reused phase2/phase3 import and result-page design direction as phase4 reference baseline

## Added Files

- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台单表快捷导入映射规则专题方案.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期导入模板字段级映射与校验规则清单.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期图片模块字段与校验规则清单.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/02_交互与组件/2026-04-21_四期图片模块前端交互与结果反馈方案.md`

## Key Decisions

- single-sheet import remains the frontend main entry and maps back into the layered internal structure
- `order_line` is generated before prevalidation and does not get its own physical sheet
- `goods_line` remains the factual goods source while `order_line` carries first-round display snapshots
- image packaging stays separate from XLSX data import and uses a waybill-package -> store-package hierarchy
- image frontend flow reuses the phased import-result-page design pattern instead of opening a second unrelated result system
