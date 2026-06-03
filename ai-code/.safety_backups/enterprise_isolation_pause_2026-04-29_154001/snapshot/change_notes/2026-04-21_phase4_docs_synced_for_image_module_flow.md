# 2026-04-21 phase4 docs synced for image module flow

## Summary

- added image module end-to-end flow into phase4 docs
- clarified import flow, preview flow, and export flow
- clarified layered feedback for waybill package, store package, and individual images

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## Key Decisions

- image import starts from a waybill-level package and resolves down to `customer_line`
- image preview is read from parsed metadata and image access paths, not raw zip files
- export supports both store-level package and waybill-level aggregated package
- import results should be readable at waybill package, store package, and single-image levels
