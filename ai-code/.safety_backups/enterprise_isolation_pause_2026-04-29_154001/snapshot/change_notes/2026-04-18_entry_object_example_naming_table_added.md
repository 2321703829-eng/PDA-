# 2026-04-18 entry object example naming table added

## What Changed

- Expanded [四类主单统一页面结构规范草稿](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/00_四类主单统一页面结构规范草稿.md) with a full example naming table for:
  - `menu_*`
  - `action_*`
  - `view_*`
  - `client_action_*`
  - client action tags
- Added example entries covering:
  - inbound
  - outbound
  - inventory count
  - relocation
  - pending exception handling

## Why

- The previous section had already defined naming principles and object relationships.
- The next useful step was to provide a concrete reference table so future implementation can align around one naming rhythm instead of inventing identifiers ad hoc.
- This also improves consistency between ordinary Odoo entry objects and execution-page client actions.

## Current Decision

- Entry objects should keep a unified `logistics_wms` naming family.
- Main-document objects remain object-centered.
- Waiting-task objects remain `waiting_*` centered.
- Execution-page objects remain `*_execution` centered.
- Exception-related entry objects remain `exception_*` or `*_pending` centered.
