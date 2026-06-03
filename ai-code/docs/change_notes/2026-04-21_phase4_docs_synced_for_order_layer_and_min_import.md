# 2026-04-21 phase4 docs synced for order layer and min import

## Summary

Updated the phase4 design docs to reflect the newly confirmed structure:

- customer name is effectively store name
- document fields belong to the order layer
- one store node can contain multiple orders
- one order can contain multiple goods lines

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## What Changed

- Upgraded the target data structure from `waybill -> customer_line -> goods_line` to `waybill -> customer_line -> order_line -> goods_line`
- Clarified that `customer_line` represents the store delivery node under a waybill
- Clarified that `order_line` is now a formal business layer rather than only a later extension
- Reassigned document/order fields to `order_line`
- Reassigned goods atomic fields to `goods_line`
- Added a structured "minimum import template" field scope based on the new object hierarchy
- Kept the existing image-package and trace-sinking decisions aligned with the new four-layer structure

## Why

The latest discussion clarified the real business relationship: a waybill contains store nodes, a store node can contain multiple orders, and each order can contain multiple goods lines. The previous docs still emphasized the store-to-goods structure too heavily, so they needed to be synchronized before further implementation planning.
