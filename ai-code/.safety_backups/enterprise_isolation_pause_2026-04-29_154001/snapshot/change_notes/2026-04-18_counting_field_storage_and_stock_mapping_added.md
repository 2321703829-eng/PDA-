# 2026-04-18 counting field storage and stock mapping added

## What Changed

- Expanded [盘点单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/05_盘点与库内作业/00_盘点单状态机草稿.md) with two new sections:
  - counting field dictionary baseline and state-field storage strategy
  - counting document linkage to stock adjustment and native stock objects
- Added guidance for:
  - `state` and `difference_result` storage
  - minimal counting document fields
  - counting-line linkage to `stock.quant`
  - the relationship between discrepancy absorption and Odoo native inventory adjustment
  - the minimum field-level linkage baseline for counting documents and counting lines

## Why

- The counting topic file had already stabilized state semantics, button linkage, execution/discrepancy linkage, and page display language.
- The next useful step was to make the design more implementation-ready by clarifying how state and discrepancy result land on the model and how counting should connect back to native stock facts.

## Current Decision

- `state` remains the sole carrier of the main counting process states.
- `difference_result` remains the carrier of discrepancy-handling results.
- Counting lines should link to `stock.quant` for theoretical inventory reference.
- Discrepancy absorption should continue to return to Odoo’s native inventory-adjustment mechanism rather than building a parallel stock-fact layer.
