# 2026-04-21 phase4 full mapping and backend research added

## Summary

- added a full single-sheet field-by-field mapping table for phase4
- added a backend database and API impact research note for phase4
- connected finalized design decisions with actual module, model, controller, and service impact areas

## Added Files

- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期单表字段逐字段全量映射表.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期后端数据库与接口影响面调研稿.md`

## Key Decisions

- the full mapping table now distinguishes `waybill`, `customer_line`, `order_line`, and `goods_line` field ownership at row level
- order snapshots and goods factual fields are explicitly separated in the mapping table
- backend research now identifies likely impact areas in `logistics_dispatch`, `logistics_trace_core`, `logistics_trace_evidence`, and `logistics_web`
- the recommended backend path remains: add a single-sheet mapping layer first, then reuse the existing three-sheet prevalidation chain
