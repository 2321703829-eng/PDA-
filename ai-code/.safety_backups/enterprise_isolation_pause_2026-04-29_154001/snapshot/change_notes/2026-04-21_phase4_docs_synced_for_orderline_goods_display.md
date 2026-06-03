# 2026-04-21 phase4 docs synced for orderline goods display

## Summary

Updated the phase4 design docs to clarify the first-round display responsibility between `order_line` and `goods_line`.

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## What Changed

- Clarified that under the first-round 1:1 implementation assumption, `order_line` is still the main reading layer
- Clarified that `order_line` should directly carry the main display fields of the corresponding goods:
  - goods code
  - goods name
  - spec
  - barcode
  - uom
  - qty
  - weight
  - volume
  - goods remark
  - package type when needed
- Clarified that `goods_line` remains as a retained/extensible atomic-goods layer instead of the first-round main reading layer
- Synced page-carrying language so order detail pages can directly show goods specification, remark, and volume information

## Why

The latest discussion confirmed that the business still needs to directly read goods information such as spec, remark, and volume from the order-side workflow. The docs needed to make this explicit so the team does not incorrectly assume that such information must only be read from `goods_line` in the first round.
