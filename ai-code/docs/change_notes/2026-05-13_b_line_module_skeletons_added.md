# 2026-05-13 B line module skeletons and action chain added

## Summary

This round continued the B line implementation on top of the initial addon skeletons:
- `custom_addons/wms_task_core`
- `custom_addons/tms_dispatch_core`
- `custom_addons/bi_ops_dashboard`

## Main changes

- `wms_task_core`
  - added sequence rules for receipt, putaway, outbound, pick, check, and handover
  - added minimal action chain for `receipt -> putaway` and `outbound -> pick -> check -> handover`
  - added `stock.picking` quick actions to create and open WMS tasks
- `tms_dispatch_core`
  - added sequence rules for dispatch, driver task, signoff receipt, and delivery exception
  - added minimal action chain for `handover -> dispatch order -> driver task -> signoff / exception`
  - added handover-side dispatch entry by inheriting `wms.handover.order`
- `bi_ops_dashboard`
  - added minimal daily KPI, exception, and cost-profit snapshot generation methods
  - added basic window actions and forms for snapshot entry points

## Why

The design phase for B line had already been narrowed enough to start implementation. The highest-value next step was to move from static model skeletons to executable task flow skeletons so later business logic can be filled in incrementally instead of repeatedly restructuring addon boundaries.

## Impact

- B line now has runnable model-level action scaffolding rather than only static tables and views
- WMS, TMS, and BI can continue to evolve independently inside their own addons
- existing logistics base objects and route planning draft objects were still reused instead of duplicated

## Follow-up

- fill the detailed business constraints for task generation and state guards
- connect ERP-side source data after A line fields and menus are ready
- install and test these three addons in the target Odoo environment

## Runtime note

- first install attempt on `odoo_logistics_webtest_v19` failed in `tms_dispatch_core/views/logistics_route_planning_views.xml`
- cause: the embedded route-stop child view still used `tree` syntax and was rejected by current Odoo 19 view validation
- fix applied: switched the child view to `list` syntax before rerunning module install
- shared deployment to `192.168.0.17:19129` then exposed a second runtime compatibility issue in `wms_task_core`
- cause: `wms.outbound.task.action_generate_pick_task` assumed `stock.move.restrict_lot_id` existed, but the shared Odoo 19 stock model does not provide that field
- fix applied: pick-line generation now checks the move schema first and falls back to `lot_id = False` when lot restriction is unavailable
