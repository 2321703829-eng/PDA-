# 2026-04-23 Phase4 New DB Install Blockers Fixed

## Objective

Fix blockers discovered while rebuilding a fresh phase-4 development database.

## Issues Fixed

### 1. `logistics_dispatch` menu install blocker

Problem:

- `logistics_dispatch_menus.xml` referenced:
  - `action_logistics_import_task`
  - `action_logistics_import_source_file`
- these actions were not defined in the current module data set
- fresh database installation failed while loading menu XML

Fix:

- removed those menu entries from the current first-round menu file
- kept the first-round install path aligned with the reduced scope

### 2. `logistics_web` label sync install blocker

Problem:

- `ui_label_sync.py` always wrote menu and action labels with `lang="zh_CN"`
- fresh databases do not necessarily have `zh_CN` installed yet
- installation failed with `Invalid language code: zh_CN`

Fix:

- added a language existence check before writing translated labels
- label sync now degrades safely on fresh databases without Chinese language installed

## Result

After these fixes:

- `odoo_logistics_phase4_v1` was initialized successfully
- `logistics_base`, `logistics_dispatch`, and `logistics_web` installed successfully in the new database
