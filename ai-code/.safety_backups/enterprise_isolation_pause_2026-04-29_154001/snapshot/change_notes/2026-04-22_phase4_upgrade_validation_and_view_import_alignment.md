# 2026-04-22 Phase4 Upgrade Validation And View Import Alignment

## Summary

- ran real Odoo upgrade validation for:
  - `logistics_base`
  - `logistics_dispatch`
  - `logistics_web`
- aligned the current XML views, menus, and import mappings with the newly landed phase4 model skeleton
- confirmed ORM initialization, migration scripts, XML loading, menu binding, and import mapping data loading all pass on the local dev database

## Upgrade Commands

```bash
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_base,logistics_dispatch --stop-after-init
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_base,logistics_dispatch,logistics_web --stop-after-init
```

## Main Alignment Work

### 1. `logistics_base`

- expanded `res.partner` logistics page with the newly added customer/base fields
- expanded `hr.employee` logistics page with organization and employee-status fields
- added a new profile view bundle for:
  - `logistics.customer.profile`
  - `logistics.store.profile`
  - `logistics.driver.profile`
  - `logistics.vehicle.profile`
  - `logistics.product.unit`
- added direct menu entries under existing Contacts / HR / Fleet / Stock menu trees

### 2. `logistics_dispatch`

- added a new view bundle for:
  - `logistics.driver.dispatch.state`
  - `logistics.vehicle.dispatch.state`
  - `logistics.import.task`
  - `logistics.import.source.file`
- added new scheduling/import menu entries for dispatch states and import logs
- expanded waybill / customer-line / goods-line / order-line views to expose the newly added snapshot and business fields

### 3. `logistics_web`

- extended `base_import.mapping` coverage for newly added dispatch fields, including:
  - waybill group / org / warehouse / route / remark snapshots
  - customer-line node number / contact / address / stop-seq / access flags / upstairs count
  - goods-line external product code / product name / snapshot spec / doc qty / amount / unsettled amount

## Result

- module upgrade passed
- ORM initialization passed
- migration scripts executed
- XML views and menus loaded successfully
- import mapping data loaded successfully

## Residual Warnings

- manifests still miss the `author` key
- Odoo 19 warns that `_sql_constraints` should move toward the newer `model.Constraint` style
- translated stored related field warnings remain for `product.template.product_name`

These warnings do not block upgrade, but they should be cleaned up in a later normalization pass.
