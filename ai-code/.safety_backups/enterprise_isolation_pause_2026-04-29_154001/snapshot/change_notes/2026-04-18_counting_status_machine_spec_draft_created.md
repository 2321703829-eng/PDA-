# 2026-04-18 counting status machine spec draft created

## What Changed

- Created a new warehouse-topic spec draft:
  - [盘点单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/05_盘点与库内作业/00_盘点单状态机草稿.md)
- Consolidated previously confirmed discussion results into a dedicated counting-document state-machine document, covering:
  - the phase-1 five-state main flow
  - the role of `reviewing`
  - discrepancy-result field guidance
  - the “no partial_done main state” boundary
  - the “no repeated adjustment on the same done document” boundary
  - the current decision not to prioritize supplementary exception states for counting in phase 1
- Updated the master discussion draft index so counting state-machine topics now have an explicit topic-file destination.

## Why

- The counting state-machine discussion had already become stable enough to stop living only inside the master discussion draft.
- A separate topic file will make later refinement easier for:
  - counting-process review
  - discrepancy-handling review
  - page/action design
  - future model and field design

## Current Decision

- The counting document should now be treated as the dedicated reference for warehouse counting state-machine design.
- Future counting state-machine refinements should continue in this topic file first, while the master discussion draft keeps only summary and index responsibilities.
