# 2026-04-22 Driver Management Frontend Align To Dispatch Profile Models

## What Changed

- rewrote `logistics_web` driver service payloads to read from:
  - `logistics.driver.profile`
  - `logistics.driver.dispatch.state`
  - current related `fleet.vehicle`
  - current related `stock.warehouse`
  - current related `logistics.dispatch.batch`
- removed old frontend dependence on:
  - `has_own_vehicle`
  - historical batch-only vehicle lookup as the primary display source
  - persisted local mock mode as the default page source
- rebuilt the driver management OWL action and template to show:
  - current dispatch status
  - current standby warehouse
  - current collaborative vehicle
  - current batch
  - night-shift willingness
  - driver code and profile-based overview fields

## Root Cause

- backend models had been upgraded, but the `logistics_web` driver page still rendered old frontend DTO assumptions and old mock-oriented field names
- this made the page look like it had not been updated, even though the underlying models and Odoo views were already changed

## Verification

- Python syntax compiled via in-memory `compile(...)`
- `node --check` passed for `driver_management_action_v2.js`
- XML parse passed for `driver_management_templates_safe.xml`
- module upgrade passed:
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_web --stop-after-init`

## Notes

- there is still no separate custom `车辆管理` client page in `logistics_web`
- vehicle information is now updated inside the driver page and continues to exist in Odoo backend list/form views
