# 2026-04-18 counting state record linkage and display rules added

## What Changed

- Expanded [盘点单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/05_盘点与库内作业/00_盘点单状态机草稿.md) with two new sections:
  - counting state to execution-record linkage matrix
  - counting detail/list state display rules
- Added:
  - a main-state vs counting execution / discrepancy-result / adjustment-result linkage table
  - phase-1 guidance for how each counting main state corresponds to counting completion and discrepancy handling
  - page-display guidance for list pages, detail headers, filters, execution-record areas, and discrepancy-info areas

## Why

- The counting topic file already defined the state machine and button/state linkage.
- The next useful step was to connect:
  - state machine -> execution/discrepancy results
  - state machine -> visible page language
- This creates a clearer bridge from counting-process rules to actual page implementation and review.

## Current Decision

- `counting` is primarily carried by counting execution records.
- `reviewing` means the counting action is complete but discrepancy results are still pending confirmation or absorption.
- `done` means counting records, discrepancy confirmation, and adjustment absorption are all complete.
- On pages, main state remains the primary label, while discrepancy-result signals remain supplementary labels.
