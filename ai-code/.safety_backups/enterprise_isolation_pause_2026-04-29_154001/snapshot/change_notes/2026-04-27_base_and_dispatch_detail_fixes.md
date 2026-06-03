# 2026-04-27 Base And Dispatch Detail Fixes

## Objective

- Fix `goods_line_v2` runtime failure caused by searching non-stored business-key fields.
- Tighten `logistics_base` and `route planning / master data change log` ACLs to reduce accidental or unauthorized mutation.
- Add backend consistency guards for `order_line` and `goods_line` to block cross-waybill linking errors.

## Scope

- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_goods_line_v2.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_order_line.py`
- `custom_addons/logistics_dispatch/security/ir.model.access.csv`
- `custom_addons/logistics_base/security/ir.model.access.csv`

## Changes

1. `goods_line_v2` customer-line resolution no longer searches non-stored `partner_no / partner_name`.
   - Reused the customer-line model's partner resolution helpers.
   - Switched final customer-line lookup to stored `partner_id + waybill_id.name`.

2. `order_line / goods_line` cross-layer consistency constraints were added.
   - `order_line.customer_line_id` must belong to the same `waybill_id`.
   - `goods_line.order_line_id` must belong to the same waybill as `customer_line_id`.
   - If `order_line.customer_line_id` is already set, it must match the target `goods_line.customer_line_id`.

3. `logistics_base` ACLs were tightened.
   - `base.group_user` is now read-only on customer/store/product-unit/driver/vehicle profile models.
   - `group_logistics_profile_manager` keeps create/write access for controlled maintenance.

4. `logistics_dispatch` route-planning and audit-log ACLs were tightened.
   - `base.group_user` is now read-only on `logistics.route.planning.batch`, `logistics.route.planning.stop.line`, and `logistics.master.data.change.log`.
   - `group_logistics_dispatch_manager` keeps create/write access for route-planning drafts.
   - `logistics.master.data.change.log` stays read-only to preserve audit credibility.

## Verify

- `python .\\odoo-bin -c .\\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_base,logistics_dispatch --stop-after-init`
- AST parse passed for:
  - `logistics_dispatch_waybill_customer_goods_line_v2.py`
  - `logistics_dispatch_waybill_order_line.py`
- CSV parse passed for:
  - `logistics_base/security/ir.model.access.csv`
  - `logistics_dispatch/security/ir.model.access.csv`
- Odoo shell smoke passed:
  - goods line created by `waybill_no + customer_no` resolved to the expected `customer_line_id`
  - regular internal user write on `logistics.driver.profile` was denied
  - regular internal user write on `logistics.route.planning.batch` was denied
  - regular internal user write on `logistics.master.data.change.log` was denied
  - mismatched `order_line.waybill_id / customer_line_id` was blocked by `ValidationError`
  - mismatched `goods_line.order_line_id / customer_line_id` was blocked by `ValidationError`

## Risks

- `waybill.customer.line / goods.line / order.line` ACLs are still broader than the main chain objects. This round only added backend consistency guards, not a full ownership/role redesign for detail lines.
- `route planning stop line` uniqueness protection was not added in this round; duplicate stop order / duplicate waybill-in-batch risks still need a dedicated follow-up.
