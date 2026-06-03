# 2026-04-21 phase4 docs synced for current data structure

## Summary

Synchronized the phase4 design docs again so they reflect the latest agreed data-structure understanding.

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## What Changed

- Added an explicit "current data structure" section into the phase4 master outline
- Clarified that the primary import result should first form `waybill -> customer_line -> goods_line`
- Clarified that `customer_line` represents the customer/store delivery node under a waybill
- Reduced emphasis on order-level extension and restated that current phase priority is customer auto-mount under the waybill
- Synced the import-template topic with the same object hierarchy and acceptance target
- Kept the previously confirmed single-sheet quick import and separate image-package direction aligned with the updated structure wording

## Why

The latest discussion clarified that the current business priority is not "customer and order" first, but "waybill and customer node" first. The docs needed to reflect that the core structure after import is the automatic mounting of customer nodes under a waybill, with later extensions built on top of that stable hierarchy.
