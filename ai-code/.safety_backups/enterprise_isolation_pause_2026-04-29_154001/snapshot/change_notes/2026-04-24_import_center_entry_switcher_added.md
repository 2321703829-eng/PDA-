# 2026-04-24 Import Center Entry Switcher Added

## What Changed

- Added an in-page entry switcher to the import center so users can directly switch between:
  - `运单导入`
  - `客户明细导入`
  - `货物明细导入`
- Extended `SOURCE_MODEL_CONFIG` with dedicated import-center action xmlids for each source model.
- Added client-side action routing from the import center page to the matching source-specific import center.

## Why

- Left-side submenu visibility was not a reliable discovery path for users.
- The import center already supports multiple `source_model` modes, but it lacked an explicit on-page switch entry.
- This makes customer and goods import/export preparation reachable from the same import center page without relying on submenu presentation.

## Verification

- `node --check custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- XML parse for `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`
- `logistics_web` module upgrade required for backend assets refresh
