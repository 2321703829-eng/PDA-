# 2026-04-21 phase4 docs synced for images and order mount

## Summary

Synchronized the existing phase4 design documents with the latest agreed business direction.

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## What Changed

- Refined the phase4 boundary for image capability:
  - phase4 now includes evidence image batch import, preview, and batch export
  - phase4 still excludes full object-storage platform rebuild and tenant/lifecycle strategy work
- Added the image-chain design judgment that main business data stays in three-sheet XLSX while images use a separate attachment package
- Added `order_line` as an explicit phase4 object in the design scope
- Added the requirement that `order_line` should gain `customer_line_id`
- Added the data rule that imported customer detail should auto-mount related orders primarily by `waybill + store`
- Added the page-carrying requirement that orders should be readable under the corresponding `customer_line`
- Synced the import-template restructure topic with the new object relationship and image package direction

## Why

The previous docs still reflected an older boundary where image storage work was fully excluded and where customer-detail-to-order mounting had not yet been absorbed into the main design line. The current business discussion has made both areas part of phase4 scope, so the design docs needed to be aligned before further specs are expanded.
