# 2026-04-24 Import Center Export Shortcuts Simplified

## What Changed

- Removed the in-page `导入入口切换` section from the import center.
- Simplified the import center export area back to a shortcut-card layout.
- Added three parallel export shortcut cards in the same section:
  - `运单标准导出`
  - `客户画像标准导出`
  - `货物画像标准导出`
- Reused the same interaction pattern as the existing waybill export shortcut:
  - enter the target list
  - select records there
  - trigger export from the list/form entry

## Why

- The entry-switcher redesign made the page heavier and visually noisy.
- The requested interaction is simpler: keep the current import-center page stable and place customer/product export shortcuts alongside the existing waybill shortcut.

## Verification

- `node --check custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- XML parse for `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`
- `logistics_web` module upgrade required for asset refresh
