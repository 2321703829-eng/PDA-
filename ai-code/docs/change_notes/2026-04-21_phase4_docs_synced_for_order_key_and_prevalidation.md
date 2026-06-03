# 2026-04-21 phase4 docs synced for order key and prevalidation

## Summary

Updated the phase4 design docs again to lock the latest implementation decisions around order keys and the single-sheet import flow.

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## What Changed

- Locked the order-key priority as:
  - `单据号`
  - `订单号`
  - `销售订单号`
- Locked that `order_line` does not need its own physical Sheet
- Locked that single-sheet import should first map into the existing three-sheet data structure and then reuse the current prevalidation module
- Locked that the in-memory `order_line` object is generated before prevalidation
- Locked that first-round multi-goods under the same order key should fail fast instead of being auto-merged
- Locked longitude and latitude as first-round hard-required fields
- Locked `scene_code` to four first-round enums:
  - `arrival`
  - `sign`
  - `exception`
  - `other`
- Clarified again that `goods_line` is the factual goods source while `order_line` remains the first-round reading layer and display snapshot

## Why

These decisions remove the remaining ambiguity around how single-sheet import should be transformed before validation, how order identity should be determined, and how evidence-context fields should be enforced in the first implementation round.
