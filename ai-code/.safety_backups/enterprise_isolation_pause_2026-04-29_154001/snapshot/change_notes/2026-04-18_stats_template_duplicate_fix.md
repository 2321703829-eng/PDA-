# 2026-04-18 Stats Template Duplicate Fix

## Objective

Fix the runtime `Missing template: "logistics_web.StatsCenterAction"` error when opening `统计图表中心`.

## Root Cause

- `custom_addons/logistics_web/static/src/xml/import_center_templates.xml` accidentally duplicated `logistics_web.ImportResultAction`.
- The same template name also exists in `custom_addons/logistics_web/static/src/xml/import_result_templates.xml`.
- In Odoo's frontend template registry, duplicate template registration can abort later registrations in the same asset bundle.
- As a result, `logistics_web.StatsCenterAction` existed on disk but was not registered at runtime.

## Outcome

- Rebuilt `import_center_templates.xml` so it only contains `logistics_web.ImportCenterAction`.
- Kept `logistics_web.ImportResultAction` only in `import_result_templates.xml`.
- Removed the duplicate-template conflict from `web.assets_backend`.

## Changed Files

- `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`

## Verify

- XML parse passed for:
  - `import_center_templates.xml`
  - `import_result_templates.xml`
  - `stats_center_templates.xml`
- Duplicate-template scan across XML files listed in `logistics_web/__manifest__.py` now returns no duplicates.

## Boundary

- This fix only repairs frontend template registration.
- No backend API, model, or permission logic was changed.
