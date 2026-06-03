# 2026-04-18 Stats Entry Alignment Fix

## Objective

Fix the issue where `统计图表中心` could open via `/odoo/action-540`, but other visible entry points were not stable.

## Root Cause

- The homepage module card was opening the stats page through a direct client-action object, while the known-good path in the running system was the persisted action `logistics_web.action_logistics_web_stats_center`.
- The `所有统计图表` menu also had child menus under it, but no explicit child entry for the stats center itself, which made the visible navigation path less stable than the direct action URL.

## Outcome

- Homepage `所有统计图表` card now opens the same persisted action xmlid used by `action-540`.
- Added an explicit `统计图表中心` child menu under `所有统计图表`.
- Updated the menu sync script so the child menu remains present after localized label synchronization.

## Changed Files

- `custom_addons/logistics_web/static/src/js/actions/home_action.js`
- `custom_addons/logistics_web/views/logistics_web_menus.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`

## Verify

- `home_action.js` passed `node --check`
- `logistics_web_menus.xml` passed XML parse
- `ui_label_sync.py` passed Python `compile(...)`

## Boundary

- This fix only aligns entry paths and menu reachability.
- It does not change stats-center business logic, APIs, or chart behavior.
