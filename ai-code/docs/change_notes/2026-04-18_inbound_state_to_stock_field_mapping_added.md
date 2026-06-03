# 2026-04-18 inbound state to stock field mapping added

## What Changed

- Expanded [入库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/02_入库管理/00_入库单状态机草稿.md) with a dedicated section for inbound state to native stock-object field mapping.
- Added guidance for:
  - inbound document to `stock.picking` linkage
  - inbound line to `stock.move` linkage
  - receive / putaway execution records to `stock.move.line` linkage
  - how inbound main states should rely on stock execution facts
  - how terminated scenarios should preserve already-created stock facts

## Why

- The inbound topic file had already become strong at the business-rule layer.
- The next useful step was to connect those rules to Odoo’s execution-layer objects so later model and view work can stay consistent with the state machine.
- This reduces the risk of drifting into a parallel warehouse fact model disconnected from native stock execution.

## Current Decision

- Inbound documents remain the business-mainline carrier.
- Native stock objects remain the execution-fact carrier.
- Main-state progression should depend on stock execution facts as much as possible.
- `terminated` should not erase already-created stock facts; it only changes how the mainline may continue.
