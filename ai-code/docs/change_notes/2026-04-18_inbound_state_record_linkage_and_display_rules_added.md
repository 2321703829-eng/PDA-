# 2026-04-18 inbound state record linkage and display rules added

## What Changed

- Expanded [入库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/02_入库管理/00_入库单状态机草稿.md) with two new sections:
  - inbound state to execution-record linkage matrix
  - inbound detail/list state display rules
- Added:
  - a main-state vs `receive record` / `putaway record` linkage table
  - phase-1 guidance for when each inbound main state should correspond to receipt vs putaway execution
  - page-display guidance for list pages, detail headers, filters, execution-record areas, and exception-info areas

## Why

- The inbound topic file already defined the state machine and button/state linkage.
- The next useful step was to connect:
  - state machine -> execution records
  - state machine -> visible page language
- This creates a clearer bridge from abstract state rules to actual page implementation and review.

## Current Decision

- `receipting` is primarily carried by receipt execution records.
- `received` means the receipt loop is complete but putaway has not formally started.
- `putawaying` is primarily carried by putaway execution records.
- On pages, main state remains the primary label, while supplementary exception status remains a secondary badge.
