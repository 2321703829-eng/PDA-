# 2026-04-18 inbound navigation rules added

## What Changed

- Expanded [入库单状态机草稿 v0.1](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/02_入库管理/00_入库单状态机草稿.md) with a dedicated section for inbound navigation rules between:
  - inbound detail pages
  - receive execution pages
  - putaway execution pages
  - pending-work views
- Added guidance for:
  - which inbound states may open receive pages
  - which inbound states may open putaway pages
  - how pending lists act as auxiliary entries
  - how execution pages should return to the inbound detail context
  - how terminated scenarios should restrict normal execution entry

## Why

- The inbound topic file had already stabilized state definitions, button/state linkage, execution-record linkage, and page display language.
- The next useful step was to make entry and return paths explicit so later detail-page buttons and action wiring can align with the same state machine.

## Current Decision

- Receive entry belongs only to `waiting_receipt / receipting`.
- Putaway entry belongs only to `received / putawaying`.
- The inbound detail page remains the primary execution entry.
- Pending-work views remain auxiliary entry points.
- After execution, the default return context should remain the same inbound detail page rather than a generic list page.
