# 2026-04-18 outbound navigation and field storage added

## What Changed

- Expanded [出库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/04_出库管理/00_出库单状态机草稿.md) with two new sections:
  - outbound navigation rules between detail and execution pages
  - outbound field dictionary baseline and state-field storage strategy
- Added:
  - rules for when detail pages may open pick/check/ship execution pages
  - rules for returning from execution pages back to the outbound detail context
  - phase-1 core fields for outbound main state and supplementary exception state
  - storage guidance for `state`, `exception_state`, and `terminated_*`

## Why

- The outbound topic file had already stabilized state semantics, button linkage, execution-record linkage, and page display language.
- The next useful step was to make entry/return paths and field storage explicit so later detail-page actions and model design can align with the same state model.

## Current Decision

- Pick entry belongs only to `waiting_pick / picking`.
- Check entry belongs only to `picked / checking`.
- Ship entry belongs only to `waiting_ship`.
- The outbound detail page remains the primary execution entry.
- `state` remains the sole carrier of main outbound process states, while `exception_state` remains the carrier of supplementary exception status.
