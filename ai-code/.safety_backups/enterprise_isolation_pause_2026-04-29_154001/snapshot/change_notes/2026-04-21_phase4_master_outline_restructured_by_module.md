# 2026-04-21 phase4 master outline restructured by module

## Summary

- rewrote the phase4 master outline into a module-oriented structure
- grouped the previous mixed content into six stable modules:
  - import
  - object structure
  - image and evidence
  - page and reading chain
  - backend and API
  - implementation and acceptance
- reduced cross-topic jumping in the outline so the document reads more like a structured program brief

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`

## Key Decisions

- kept all current phase4 conclusions but reorganized them by module instead of by mixed concern type
- preserved the current first-round core chain:
  - `waybill -> customer_line -> order_line -> goods_line`
- preserved the current first-round image boundary:
  - image business minimum attachment remains `customer_line`
