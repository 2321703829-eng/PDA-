# 2026-04-18 Stats Menu Label Encoding Fix

## Objective

Fix the garbled label shown for the new `统计图表中心` submenu under `所有统计图表`.

## Root Cause

- The submenu label added in `ui_label_sync.py` was written with mojibake text.
- During localized menu synchronization, that bad label was written into the database menu name.

## Outcome

- Added a stable overwrite path in `ui_label_sync.py` that forces the submenu label to `统计图表中心`.
- Corrected the current database value for `logistics_web.menu_logistics_web_stats_center` using Unicode-safe text.

## Changed Files

- `custom_addons/logistics_web/models/ui_label_sync.py`

## Verify

- Database check confirmed the stored label code points are:
  - `0x7edf 0x8ba1 0x56fe 0x8868 0x4e2d 0x5fc3`

## Boundary

- This fix only corrects the submenu display label.
- No stats-center logic or permissions were changed.
