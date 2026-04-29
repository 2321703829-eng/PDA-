# 2026-04-18 menu tree and action binding draft added

## What Changed

- Expanded [四类主单统一页面结构规范草稿](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/00_四类主单统一页面结构规范草稿.md) with a draft for:
  - warehouse menu-tree hierarchy
  - second- and third-level menu grouping
  - menu-to-`act_window` binding relationships
  - the handoff from list actions to execution-page client actions

## Why

- The spec had already defined naming rules for menus, actions, views, and client actions.
- The next useful step was to organize those entry objects into a coherent warehouse menu tree instead of leaving them as flat naming examples.
- This helps the future implementation stay aligned with the logistics module’s overall backend rhythm while preserving a clear distinction between document entry and execution entry.

## Current Decision

- Warehouse should enter the backend through one unified first-level module entry.
- Phase 1 should primarily use three second-level groups:
  - document center
  - pending-work center
  - exception-handling center
- Menus should mainly bind to `act_window` list/detail entries.
- Execution-page client actions should remain secondary operational entries launched from details or pending lists, not primary top-level menu destinations.
