# 2026-04-28 enterprise isolation `P1` image_package import, matching, and linking

## Summary

Implemented the next `P1` coding slice for `image_package` so the current trace/evidence/exception/waybill main line can accept packaged image imports through the existing import-task audit chain.

This slice adds:

- backend image package import wizard
- image package task list and task form
- matching and linking service
- retry path for failed image package lines
- role-aligned upload / retry boundaries

## Code changes

### 1. New service and model extensions

Added:

- `custom_addons/logistics_trace_evidence/services/image_package_import_service.py`
- `custom_addons/logistics_trace_evidence/models/logistics_image_package_import.py`

Main behavior:

- reuse `logistics.import.source.file`
- reuse `logistics.import.task`
- reuse `logistics.import.task.line`
- reuse `logistics.import.error.line`
- accept ZIP image packages
- parse file names into:
  - `waybill_no`
  - `customer_line_no`
  - `store_no`
  - `scene_code`
- match to current `waybill`
- resolve target `trace_event`
- create formal `logistics.trace.evidence`
- upload binary through existing evidence image storage path
- mark failed / manual-review lines and keep error rows

### 2. Evidence-side task fields

Extended `logistics.import.task` with image-package summary metrics:

- `matched_count`
- `unmatched_count`
- `ambiguous_count`
- `linked_count`
- `link_failed_count`
- `manual_review_count`

Extended `logistics.import.task.line` with image-package-specific fields such as:

- `package_entry_name`
- `source_filename`
- `scene_code`
- `capture_time`
- `waybill_no`
- `customer_line_no`
- `store_no`
- `matched_waybill_id`
- `matched_customer_line_id`
- `match_status`
- `match_method`
- `selected_trace_event_id`
- `linked_evidence_id`
- `image_access_key`
- `link_status`
- `retry_count`

### 3. Views and menu entries

Added:

- `custom_addons/logistics_trace_evidence/views/logistics_image_package_import_views.xml`

This provides:

- image package upload wizard
- image package task action
- image package task tree / form / search views
- task-line retry button
- linked-evidence jump entry
- menu entries under the existing import-center branch

### 4. Access and record-rule alignment

Updated:

- `custom_addons/logistics_trace_evidence/security/ir.model.access.csv`
- `custom_addons/logistics_trace_evidence/security/logistics_trace_evidence_security.xml`

Added wizard access for:

- `base.group_system`
- `logistics_dispatch.group_logistics_dispatch_manager`
- `logistics_dispatch.group_logistics_import_manager`
- `logistics_trace_core.group_logistics_image_field_operator`

Added image-package read-all rules for:

- `base.group_system`
- `logistics_dispatch.group_logistics_dispatch_manager`
- `logistics_trace_evidence.group_logistics_image_auditor`

across:

- `logistics.import.source.file`
- `logistics.import.task`
- `logistics.import.task.line`
- `logistics.import.error.line`

UI tightening:

- upload menu kept for actual upload-capable roles only
- retry buttons kept for dispatch manager / import manager / image auditor / system only

## Verification

### Static checks

- XML parse check passed for `logistics_image_package_import_views.xml`
- Python source compile check passed by direct `compile(...)` parsing for:
  - `logistics_image_package_import.py`
  - `image_package_import_service.py`

### Runtime upgrade

Ran module upgrade on `odoo_logistics_dev`:

- `logistics_trace_evidence`

Upgrade completed successfully and reloaded:

- `logistics_trace_evidence`
- dependent downstream modules in the upgrade chain

### Smoke test

Executed an Odoo shell smoke test against `odoo_logistics_dev` under savepoint rollback:

- selected an existing waybill with a submitted trace event
- generated an in-memory ZIP with a file named by current matching rules
- called `ImagePackageImportService.import_zip(...)`

Observed result:

- task created successfully
- task status = `success`
- line status = `success`
- match status = `matched`
- link status = `linked`
- waybill matched successfully
- formal evidence created successfully
- evidence image access key generated successfully

### Role verification

Executed a temporary role-verification script under savepoint rollback for four role shapes:

- readonly
- image field operator
- dispatch manager
- image auditor

Observed import permission result:

- readonly: denied
- image field operator: allowed
- dispatch manager: allowed
- image auditor: denied

Observed retry permission result:

- readonly: denied
- image field operator: denied
- dispatch manager: allowed
- image auditor: allowed

These results match the current lightweight `P1` permission design.

## Delivery notes

Added delivery-facing docs:

- `专题设计/企业隔离设计/05_提交包/2026-04-28_企业隔离P1本轮已完成能力.md`
- `专题设计/企业隔离设计/05_提交包/2026-04-28_企业隔离P1本轮剩余待办项.md`

## Remaining gaps

Not done in this slice:

- frontend import-center page integration for image package upload
- richer manual-review / manual relink UI
- production-grade bulk retry / audit dashboard
- actual business-account page-level manual verification in browser
