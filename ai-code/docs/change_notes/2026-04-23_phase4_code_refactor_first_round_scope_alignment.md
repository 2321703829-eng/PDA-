# 2026-04-23 Phase4 Code Refactor First-Round Scope Alignment

## Objective

Align the implemented Odoo models and service layer with the updated phase-4 first-round scope:

- keep only driver and vehicle profile capability
- defer dispatch state and assignment history tables
- flatten `logistics.product.unit` to one row per sales unit
- store structured address data with geo coordinates

## Main Changes

### 1. `logistics_base`

- Refactored `logistics.product.unit` into a single-unit-per-row structure.
- Removed small/middle/large duplicated barcode and price fields.
- Added unified `standard_price`, `purchase_price`, and `retail_price`.
- Updated the unique constraint to `product_tmpl_id + spec_desc + sale_unit_name`.
- Changed store profile `longitude` / `latitude` to float fields.
- Added `address_region_json` to store profile.
- Synced base profile views to the new product-unit and address fields.

### 2. `logistics_dispatch`

- Added `address_region_json_snapshot` to waybill customer-line snapshot data.
- Changed snapshot longitude / latitude to float fields.
- Removed first-round dispatch runtime models and entry points:
  - `logistics.driver.dispatch.state`
  - `logistics.vehicle.dispatch.state`
  - `logistics.driver.assignment.history`
  - `logistics.vehicle.assignment.history`
  - `logistics.dispatch.state.change.log`
- Removed related XML views, menu entries, access rules, and migration index setup.

### 3. `logistics_web`

- Refactored driver management and vehicle management services.
- Replaced reads from dispatch-state tables with runtime derivation from:
  - profile data
  - current active `logistics.dispatch.batch`
  - record `active` state
- Driver and vehicle overview/filter payloads now compute:
  - current batch
  - current warehouse
  - current driver / vehicle
  - current status
  - shift type for drivers

## Verification

- Searched the codebase to confirm old small/middle/large product-unit fields were removed.
- Searched the codebase to confirm dispatch state / assignment history model references were removed from active code paths.
- Performed Python syntax compilation and XML parsing on the touched files after refactor.

## Risk Notes

- Module upgrade is still required to apply model/table changes inside Odoo.
- Existing development databases may still retain old physical tables until upgrade or cleanup is executed.
