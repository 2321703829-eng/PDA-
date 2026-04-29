# 2026-04-28 Enterprise Isolation DB Entry Guard And Permission Real Account Regression

## Background

After the first local `P0` tenant validation was built around `kebi / tenant_kebi`, two follow-up items became the immediate focus:

- close the database-management entrypoints for the tenant validation instance
- run a first-round real-account regression for the current `P1` lightweight role design

## What changed

### 1. Database entry guard

Added a lightweight guard controller in `logistics_web`:

- file: `custom_addons/logistics_web/controllers/database_guard.py`

Current behavior for the dedicated `tenant_kebi` validation instance:

- valid tenant host hitting `/web/database/selector` is redirected back to `/web/login`
- `/web/database/manager` is blocked
- `/web/database/list` is blocked through error response

This closes the selector/manager/list path for the effective tenant entry.

### 2. Real-account permission regression

Recorded the first real-account regression result for the three current core roles:

- readonly viewer
- image field operator
- dispatch / manager

The regression confirmed the current lightweight `P1` permission boundaries are basically aligned with design.

## Synced docs

- `专题设计/企业隔离设计/02_验收与联调/2026-04-28_企业隔离P1权限实账号回归记录.md`
- `专题设计/企业隔离设计/02_验收与联调/README.md`
- `专题设计/企业隔离设计/README.md`
