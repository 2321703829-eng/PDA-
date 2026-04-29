# 2026-04-18 menu permission layers and visibility draft added

## What Changed

- Expanded [四类主单统一页面结构规范草稿](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/00_四类主单统一页面结构规范草稿.md) with a draft for:
  - menu permission layering
  - role-based menu visibility
  - the boundary between menu visibility, page access, and action execution
  - recommended visibility ranges for the warehouse menu tree

## Why

- The spec had already defined menu hierarchy and action binding.
- The next useful step was to prevent future menu design from implicitly becoming the only permission model.
- Clarifying menu visibility early helps the warehouse module stay operable for frontline users while keeping exception handling and higher-risk areas appropriately restricted.

## Current Decision

- Permissions should be thought of in three layers:
  - menu visibility
  - page access
  - action execution
- Main document menus can remain broadly visible to warehouse-related users.
- Pending-work menus should stay visible to execution roles.
- Exception-handling menus should prefer supervisor, exception-handling, and admin roles rather than broad operator visibility.
