# 2026-04-18 outbound status machine spec draft created

## What Changed

- Created a new warehouse-topic spec draft:
  - [出库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/04_出库管理/00_出库单状态机草稿.md)
- Consolidated previously confirmed discussion results into a dedicated outbound state-machine document, covering:
  - the phase-1 eight-state main flow
  - cancel boundaries
  - the split between main state and supplementary exception state
  - pick/check failure handling
  - the boundary between `waiting_ship`, `done`, and pre/post-shipment exceptions
  - the phase-1 expectation for pending-exception views and exception info areas
- Updated the master discussion draft index so outbound state-machine topics now have an explicit topic-file destination.

## Why

- The outbound state-machine discussion had already become stable enough to stop living only inside the master discussion draft.
- A separate topic file will make later refinement easier for:
  - state/transition review
  - outbound page/action design
  - execution-page entry refinement
  - model and field design

## Current Decision

- The outbound document should now be treated as the dedicated reference for warehouse outbound state-machine design.
- Future outbound state-machine refinements should continue in this topic file first, while the master discussion draft keeps only summary and index responsibilities.
