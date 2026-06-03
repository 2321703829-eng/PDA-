# 2026-05-13 b line round2 round3 progress added

## Summary

- extended B-line round 2 with WMS inventory operations for count, adjustment, and warehouse return handling
- extended TMS dispatch and driver-task flow with warehouse-arrival, delivering-node, freight-line generation, and related-waybill actions
- extended B-line round 3 with BI order, warehouse, and dispatch dashboard snapshots plus drill-down actions
- added reverse lookup buttons from existing `waybill` pages into new WMS and TMS records

## Files

- `custom_addons/wms_task_core/models/wms_inventory_models.py`
- `custom_addons/wms_task_core/models/logistics_dispatch_waybill.py`
- `custom_addons/wms_task_core/views/logistics_dispatch_waybill_views.xml`
- `custom_addons/wms_task_core/views/wms_task_views.xml`
- `custom_addons/wms_task_core/data/sequence_data.xml`
- `custom_addons/wms_task_core/security/ir.model.access.csv`
- `custom_addons/tms_dispatch_core/models/logistics_dispatch_waybill.py`
- `custom_addons/tms_dispatch_core/models/tms_dispatch_models.py`
- `custom_addons/tms_dispatch_core/views/logistics_dispatch_waybill_views.xml`
- `custom_addons/tms_dispatch_core/views/tms_dispatch_views.xml`
- `custom_addons/bi_ops_dashboard/models/bi_snapshot_models.py`
- `custom_addons/bi_ops_dashboard/views/bi_snapshot_views.xml`
- `custom_addons/bi_ops_dashboard/security/ir.model.access.csv`

## Verify

- python AST parse passed
- XML parse passed

## Notes

- this round focuses on finishing B-line round 2 operational closure first, then pushing B-line round 3 BI and legacy-logistics linkage forward
