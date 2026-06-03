# 2026-04-23 Add One-Click Profile Entry From Employee And Vehicle Master

## Summary

- Added a one-click driver profile entry on `hr.employee` forms.
- Added a one-click vehicle profile entry on `fleet.vehicle` forms.
- The button behavior is unified:
  - open the existing profile if it already exists
  - otherwise create the linked profile automatically and open it

## Files

- `custom_addons/logistics_base/models/hr_employee.py`
- `custom_addons/logistics_base/models/fleet_vehicle.py`
- `custom_addons/logistics_base/views/hr_employee_views.xml`
- `custom_addons/logistics_base/views/fleet_vehicle_views.xml`
- `custom_addons/logistics_base/__manifest__.py`

## Behavior

- Employee form now shows a `司机画像` stat button when `logistics_role = driver`.
- Vehicle form now shows a `车辆画像` stat button in the native fleet button box.
- New profile records are initialized with the current master record as the linked object.
- Driver profile auto-fill includes basic name, phone, and residence-region hints when available.

## Verify

- Python compile passed for:
  - `custom_addons/logistics_base/models/hr_employee.py`
  - `custom_addons/logistics_base/models/fleet_vehicle.py`
- XML parse passed for:
  - `custom_addons/logistics_base/views/hr_employee_views.xml`
  - `custom_addons/logistics_base/views/fleet_vehicle_views.xml`
- Odoo upgrade passed:
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_base --stop-after-init`
