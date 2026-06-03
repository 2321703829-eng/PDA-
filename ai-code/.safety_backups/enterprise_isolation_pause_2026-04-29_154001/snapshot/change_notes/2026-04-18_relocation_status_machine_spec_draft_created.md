# 2026-04-18 relocation status machine spec draft created

## What Changed

- Created a new warehouse-topic spec draft:
  - [移位单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/05_盘点与库内作业/01_移位单状态机草稿.md)
- Consolidated previously confirmed discussion results into a dedicated relocation-document state-machine document, covering:
  - the phase-1 five-state main flow
  - cancel boundaries
  - the “execution failure stays in executing” rule
  - the “no partial_done main state” boundary
  - the “done should be corrected by new relocation or adjustment, not rollback” boundary
  - the lightweight exception-info-area recommendation
- Updated the master discussion draft index so relocation state-machine topics now have an explicit topic-file destination.

## Why

- The relocation state-machine discussion had already become stable enough to stop living only inside the master discussion draft.
- A separate topic file will make later refinement easier for:
  - relocation-process review
  - page/action design
  - model and field design
  - stock-object linkage design

## Current Decision

- The relocation document should now be treated as the dedicated reference for warehouse relocation state-machine design.
- Future relocation state-machine refinements should continue in this topic file first, while the master discussion draft keeps only summary and index responsibilities.
