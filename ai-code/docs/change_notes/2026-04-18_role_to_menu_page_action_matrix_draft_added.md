# 2026-04-18 role to menu page action matrix draft added

## What Changed

- Expanded [四类主单统一页面结构规范草稿](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/00_四类主单统一页面结构规范草稿.md) with a draft matrix covering:
  - role-to-menu visibility
  - role-to-page access
  - role-to-action execution
- Added a baseline five-role model:
  - warehouse operator
  - warehouse supervisor/lead
  - exception-handling role
  - warehouse administrator
  - read-only query role

## Why

- The spec had already defined menu hierarchy and permission layering.
- The next useful step was to turn those layered ideas into a concrete matrix the team can use when aligning menus, actions, view visibility, and later security rules.
- This reduces the risk of permission design remaining too abstract while implementation starts.

## Current Decision

- Phase 1 should use a five-role baseline matrix.
- Menu, page, and action permissions should continue to be treated as separate layers.
- Operators focus on routine execution, supervisors on management and key actions, exception roles on exception closure, admins on global coverage, and read-only roles on viewing only.
