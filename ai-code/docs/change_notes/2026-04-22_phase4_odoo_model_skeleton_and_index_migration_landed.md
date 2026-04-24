# 2026-04-22 Phase4 Odoo Model Skeleton And Index Migration Landed

## Summary

- translated the phase4 database implementation draft into addon-level Odoo model skeletons
- added `_sql_constraints`, access rows, sequence records, and manual index migrations
- split the landing by module boundary:
  - `logistics_base` for official master-data extensions and profile tables
  - `logistics_dispatch` for execution chain, current dispatch state, assignment history, import logs, and audit logs

## Updated Files

### `custom_addons/logistics_base`

- `__manifest__.py`
- `models/__init__.py`
- `models/res_partner.py`
- `models/hr_employee.py`
- `models/stock_warehouse.py`
- `models/selection_options.py`
- `models/product_template.py`
- `models/fleet_vehicle.py`
- `models/logistics_customer_profile.py`
- `models/logistics_store_profile.py`
- `models/logistics_product_unit.py`
- `models/logistics_driver_profile.py`
- `models/logistics_vehicle_profile.py`
- `security/ir.model.access.csv`
- `migrations/19.0.1.1.0/post-migration.py`

### `custom_addons/logistics_dispatch`

- `__manifest__.py`
- `models/__init__.py`
- `models/selection_options.py`
- `models/logistics_dispatch_wave.py`
- `models/logistics_dispatch_batch.py`
- `models/logistics_dispatch_waybill.py`
- `models/logistics_dispatch_waybill_customer_line_v2.py`
- `models/logistics_dispatch_waybill_order_line.py`
- `models/logistics_dispatch_waybill_customer_goods_line_v2.py`
- `models/logistics_dispatch_dispatch_state.py`
- `models/logistics_dispatch_assignment_history.py`
- `models/logistics_import_log.py`
- `models/logistics_dispatch_import_support.py`
- `data/sequence_data.xml`
- `security/ir.model.access.csv`
- `migrations/19.0.1.1.0/post-migration.py`

## Main Additions

### 1. `logistics_base` landed the master-data and profile layer

- extended `res.partner`, `hr.employee`, `product.template`, and `fleet.vehicle`
- added:
  - `logistics.customer.profile`
  - `logistics.store.profile`
  - `logistics.product.unit`
  - `logistics.driver.profile`
  - `logistics.vehicle.profile`
- added uniqueness constraints for external customer code, external product code, and one-to-one profile ownership

### 2. `logistics_dispatch` landed the execution and dispatch state layer

- expanded:
  - `logistics.dispatch.wave`
  - `logistics.dispatch.batch`
  - `logistics.dispatch.waybill`
  - `logistics.dispatch.waybill.customer.line`
  - `logistics.dispatch.waybill.order.line`
  - `logistics.dispatch.waybill.customer.goods.line`
- added:
  - `logistics.driver.dispatch.state`
  - `logistics.vehicle.dispatch.state`
  - `logistics.driver.assignment.history`
  - `logistics.vehicle.assignment.history`

### 3. import and audit logs were formalized

- added:
  - `logistics.import.source.file`
  - `logistics.import.task`
  - `logistics.import.task.line`
  - `logistics.import.error.line`
  - `logistics.master.data.change.log`
  - `logistics.dispatch.state.change.log`
- added dedicated sequence records for source-file number and import-task number

### 4. manual indexes were prepared as migration scripts

- `logistics_base` migration now creates profile and product-unit lookup indexes
- `logistics_dispatch` migration now creates:
  - dispatch-state availability indexes
  - assignment-history trace indexes
  - execution-chain join indexes
  - import-task / import-error lookup indexes

## Verify

- ran `python -m py_compile` against the newly added and rewritten model files
- syntax check passed

## Notes

- this turn focused on model skeletons, constraints, access, and migration readiness
- existing XML views were intentionally not fully redesigned in this turn; the implementation stays additive where possible so current dispatch pages are less likely to break during the next upgrade cycle
