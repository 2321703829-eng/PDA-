# 2026-04-21 phase4 docs synced for mapping manifest and trace scope

## Summary

Updated the phase4 design docs again to lock the newly agreed implementation-level rules.

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## What Changed

- Locked `customer_line_no` as an internal required stable key while allowing first-round auto-generation during import
- Locked first-round single-sheet aggregation rules:
  - waybill aggregation by `waybill_no`
  - customer-line aggregation by `customer_line_no`, else `waybill_no + store_no`, else `waybill_no + customer_no`
- Locked the first-round conflict rule that shared-field conflicts should error instead of auto-overwrite
- Locked the first-round image manifest minimum fields:
  - required: `file_name`, `waybill_no`, `store_no`, `scene_code`, `image_seq`
  - optional: `customer_line_no`, `taken_at`, `remark`, `source_doc_no`
- Locked first-round image matching priority:
  - `customer_line_no`
  - otherwise `waybill_no + store_no`
- Locked that trace sinking to `customer_line` should happen in the first round, but only as a minimal viable scope

## Why

The previous docs had already aligned on direction, but these core rules were still open enough to slow implementation planning. The latest sync turns them into explicit design constraints so backend, import, and page work can now decompose around a more stable baseline.
