# 2026-04-18 page blocks to module file mapping draft added

## What Changed

- Expanded [四类主单统一页面结构规范草稿](D:/Desktop/Odoo/ai-code/仓管模块设计/01_模块设计/00_四类主单统一页面结构规范草稿.md) with a draft mapping from page blocks to actual module ownership and file naming.
- Added guidance for:
  - which modules should own ordinary list/detail/search pages
  - which module should own execution-page shells
  - suggested directory layering
  - suggested XML and frontend file naming directions
  - responsibility mapping between page blocks and concrete file locations

## Why

- The spec had already clarified page structure, Odoo component mapping, and execution-page landing patterns.
- The next useful step was to reduce ambiguity around where future implementation should live.
- This helps prevent two common problems:
  - pushing ordinary document pages too early into heavy custom web containers
  - scattering execution-page logic across multiple business modules without a shared interaction shell

## Current Decision

- Ordinary document list/detail/search pages should still primarily live in the corresponding business modules.
- Execution-page shells, unified feedback layers, and shared heavy interaction containers should primarily live in `logistics_wms_web`.
- Naming should stay object-oriented and action-oriented, and phase 1 should avoid over-fragmenting files too early.
