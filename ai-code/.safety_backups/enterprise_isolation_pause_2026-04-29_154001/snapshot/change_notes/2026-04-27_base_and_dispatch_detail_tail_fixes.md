# 2026-04-27 Base And Dispatch Detail Tail Fixes

## Objective

- Close the remaining security and data-quality tails after the base/dispatch detail repair round.
- Tighten detail-line ACLs to align with the main dispatch chain.
- Add route-planning stop-line uniqueness guards inside each planning batch.

## Scope

- `custom_addons/logistics_dispatch/security/ir.model.access.csv`
- `custom_addons/logistics_dispatch/models/logistics_route_planning_draft.py`

## Changes

1. Tightened detail-line ACLs.
   - `logistics.dispatch.waybill.customer.line`
   - `logistics.dispatch.waybill.customer.goods.line`
   - `logistics.dispatch.waybill.order.line`
   - `base.group_user` is now read-only on all three models.
   - `group_logistics_dispatch_manager` keeps create/write access for controlled maintenance.

2. Added route-planning stop-line uniqueness guards.
   - Unique `(batch_id, stop_seq)`
   - Unique `(batch_id, waybill_no)`
   - This blocks duplicate stop order and duplicate waybill rows inside the same planning batch.

## Verify

- `python .\\odoo-bin -c .\\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch --stop-after-init`
- AST parse passed for `logistics_route_planning_draft.py`
- Odoo shell smoke passed:
  - regular internal user write on `customer_line / goods_line / order_line` was denied
  - duplicate `(batch_id, stop_seq)` insert raised unique-constraint violation
  - duplicate `(batch_id, waybill_no)` insert raised unique-constraint violation

## Notes

- The first duplicate-waybill smoke script rolled back the parent batch together with the failed insert, so the initial result looked noisy. A second isolated verification confirmed the unique constraint was already working as expected.
