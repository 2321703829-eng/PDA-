# 2026-04-21 phase4 docs synced for four-sheet upgrade threshold

## Summary

Updated the phase4 design docs to add an explicit evolution boundary for when the physical import template should move from three sheets to four sheets.

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## What Changed

- Added a dedicated “four-sheet upgrade threshold” section to both docs
- Clarified that phase4 still keeps the physical template at three sheets
- Defined the concrete signals that would justify moving to four sheets later:
  - multi-goods per order becomes common
  - order-layer fields significantly expand
  - users naturally maintain order-head plus goods-lines
  - three-sheet validation and error localization degrade
  - `order_line` gains an independent lifecycle

## Why

The current design intentionally keeps physical templates lighter than the internal object model. The new threshold section makes the later evolution boundary explicit, so the team can distinguish “good reason to upgrade” from “structure looks cleaner on paper”.
