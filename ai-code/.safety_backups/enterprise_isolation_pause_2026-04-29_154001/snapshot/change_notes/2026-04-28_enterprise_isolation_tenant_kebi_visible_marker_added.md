# 2026-04-28 Enterprise Isolation tenant_kebi Visible Marker Added

## Background

During local `P0` validation, the `tenant_kebi` entry was already routable, but manual verification still relied too much on URL memory.

## What changed

- Added an obvious tenant-specific visual marker inside `tenant_kebi`.
- Updated the default company display name from `My Company` to `KEBI test tenant`.

## Purpose

- make manual login verification easier
- reduce confusion between `tenant_kebi` and other local databases
- give `P0` environment validation a visible in-system identity marker

## Synced docs

- `专题设计/企业隔离设计/02_验收与联调/2026-04-28_企业隔离P0真实环境参数登记单.md`
- `专题设计/企业隔离设计/02_验收与联调/2026-04-28_企业隔离P0_kebi租户执行清单.md`
