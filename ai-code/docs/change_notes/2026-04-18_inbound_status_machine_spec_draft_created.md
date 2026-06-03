# 2026-04-18 inbound status machine spec draft created

## What Changed

- Created a new warehouse-topic spec draft:
  - [入库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/02_入库管理/00_入库单状态机草稿.md)
- Consolidated previously confirmed discussion results into a dedicated inbound state-machine document, covering:
  - the phase-1 seven-state main flow
  - state entry/exit conditions
  - normal cancel boundaries
  - the `receipting` termination handling approach
  - the split between main state and supplementary exception state
  - phase-1 `terminated` minimum fields, reasons, permission, and display rules
- Updated the discussion draft index so inbound state-machine topics now have an explicit topic-file destination.

## Why

- The inbound state-machine discussion had become stable enough to stop living only inside the master discussion draft.
- A separate topic file makes later refinement easier for:
  - state/transition review
  - document-page behavior review
  - implementation planning
  - future field/security/detail expansion

## Current Decision

- The inbound document should now be treated as the dedicated reference for warehouse inbound state-machine design.
- Future inbound state-machine refinements should continue in this topic file first, while the master discussion draft keeps only summary and index responsibilities.
