# 2026-04-23 Vehicle Management Frontend Added For Dispatch/Profile Models

## Summary

- Added a dedicated custom vehicle management client action in `logistics_web`.
- Aligned the vehicle page structure with the current custom driver management page.
- Wired the vehicle page to `logistics.vehicle.profile` and `logistics.vehicle.dispatch.state`.
- Added vehicle management menu/action/security entry and verified module upgrade.

## Files

- `custom_addons/logistics_web/models/logistics_vehicle_service.py`
- `custom_addons/logistics_web/controllers/logistics_web_vehicle.py`
- `custom_addons/logistics_web/static/src/js/actions/vehicle_management_action_v2.js`
- `custom_addons/logistics_web/static/src/xml/vehicle_management_templates.xml`
- `custom_addons/logistics_web/models/__init__.py`
- `custom_addons/logistics_web/controllers/__init__.py`
- `custom_addons/logistics_web/views/logistics_web_actions.xml`
- `custom_addons/logistics_web/views/logistics_web_menus.xml`
- `custom_addons/logistics_web/static/src/js/actions/logistics_action_registry.js`
- `custom_addons/logistics_web/security/logistics_web_security.xml`
- `custom_addons/logistics_web/__manifest__.py`

## Behavior

- List mode supports keyword, status, warehouse, and current driver filters.
- Profile mode shows current dispatch context, capacity, execution summary, trend text blocks, recent waybills, and recent exceptions.
- Vehicle drill-through actions open related waybills and exceptions directly from the profile page.
- Vehicle data no longer depends on old driver-page DTO assumptions or mock-style fallback fields.

## Verify

- `node --check custom_addons/logistics_web/static/src/js/actions/vehicle_management_action_v2.js`
- XML parse passed for vehicle template and related menu/action/security XML files
- Python compile passed for:
  - `custom_addons/logistics_web/models/logistics_vehicle_service.py`
  - `custom_addons/logistics_web/controllers/logistics_web_vehicle.py`
- Odoo upgrade passed:
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_web --stop-after-init`
