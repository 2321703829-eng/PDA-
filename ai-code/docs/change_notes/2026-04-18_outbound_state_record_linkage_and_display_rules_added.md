# 2026-04-18 outbound state record linkage and display rules added

## What Changed

- Expanded [出库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/04_出库管理/00_出库单状态机草稿.md) with two new sections:
  - outbound state to execution-record linkage matrix
  - outbound detail/list state display rules
- Added:
  - a main-state vs `pick record` / `check record` / `ship confirm record` linkage table
  - phase-1 guidance for how each outbound main state corresponds to pick, check, and ship-confirm execution
  - page-display guidance for list pages, detail headers, filters, execution-record areas, and exception-info areas

## Why

- The outbound topic file already defined the state machine and button/state linkage.
- The next useful step was to connect:
  - state machine -> execution records
  - state machine -> visible page language
- This creates a clearer bridge from outbound process-state rules to actual page implementation and review.

## Current Decision

- `picking` is primarily carried by pick execution records.
- `picked` means the picking loop is complete but checking has not formally started.
- `checking` is primarily carried by check execution records.
- `waiting_ship` means pick and check have both completed, and the order is waiting for shipment confirmation.
- On pages, main state remains the primary label, while supplementary exception status remains a secondary badge.
