# 2026-04-21 phase4 page ia and acceptance added

## Summary

- added a phase4 page information architecture and reading-chain design note
- added a phase4 integration and acceptance checklist
- aligned both documents with phase3 page-relationship and result-page acceptance style

## Added Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-21_四期页面信息架构与阅读链方案.md`
- `ai-code/前端设计/四期前端优化设计/02_验收与联调/2026-04-21_四期联调与验收清单.md`

## Key Decisions

- phase4 reading center is no longer only the waybill header; it expands to `waybill -> customer_line -> order_line`
- image reading flows from waybill summary into `customer_line` preview, while export supports both store package and waybill package
- acceptance is organized around four chains: single-sheet import, object reading, image import/result, and image export
