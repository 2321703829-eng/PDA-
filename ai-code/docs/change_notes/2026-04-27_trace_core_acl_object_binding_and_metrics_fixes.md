# 2026-04-27 Trace Core ACL Object Binding And Metrics Fixes

## Objective

Fix the high-risk `logistics_trace_core` issues found in review v4:

- over-broad `logistics.trace.event` write/delete permissions
- incomplete `waybill / batch` object binding constraints
- trace metrics counting invalid or draft events and never producing `partial`

## What Changed

- Added `group_logistics_trace_event_manager` in `logistics_trace_core`.
- Tightened `logistics.trace.event` ACL to:
  - base internal user: read/create
  - trace manager: read/write/create
  - no unlink for either group
- Restricted the dedicated trace menu/action to the trace manager group.
- Disabled direct raw trace form opening from the `logistics_web` waybill debug section.
- Reworked `logistics.trace.event` create/write flow:
  - non-manager create always uses current user as submitter
  - non-manager cannot create `draft / invalid`
  - non-manager cannot change `submit_user_id` or `state`
  - waybill-linked trace auto-fills its batch
- Strengthened object link validation:
  - waybill trace must match the waybill batch
  - batch trace cannot directly bind a waybill
- Reworked waybill trace aggregation to only count `submitted` events.
- Added real `partial` behavior for arrive/signoff trace status.
- Reworked waybill evidence metrics to only count evidence on `submitted` trace events.

## Verify Plan

- Parse touched Python/XML files.
- Upgrade `logistics_trace_core`, `logistics_trace_evidence`, and `logistics_web`.
- Run shell smoke for:
  - non-manager write blocked
  - submitter spoofing blocked
  - mismatched waybill/batch blocked
  - invalid trace excluded from metrics
  - `partial` status appears when expected

## Verify Result

- Parse checks passed for:
  - `custom_addons/logistics_trace_core/models/logistics_trace_event.py`
  - `custom_addons/logistics_trace_core/models/logistics_dispatch_waybill.py`
  - `custom_addons/logistics_trace_evidence/models/logistics_dispatch_waybill.py`
  - `custom_addons/logistics_trace_core/security/logistics_trace_core_security.xml`
  - `custom_addons/logistics_trace_core/views/logistics_trace_event_views.xml`
  - `custom_addons/logistics_web/views/logistics_web_waybill_views.xml`
  - `custom_addons/logistics_trace_core/security/ir.model.access.csv`
- Module upgrade passed:
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_trace_core,logistics_trace_evidence,logistics_web --stop-after-init`
- Shell smoke passed on isolated sample data:
  - `owner_submitter_forced = true`
  - `owner_auto_batch_match = true`
  - `owner_write_blocked = AccessError`
  - `manager_draft_create = draft`
  - `mismatch_blocked = Waybill trace events must use the same batch as the linked waybill.`
  - `batch_waybill_blocked = Batch trace events cannot link to a specific waybill.`
  - `trace_count_after_invalid_plus_submitted = 1`
  - `latest_trace_type_after_invalid_plus_submitted = start_loading`
  - `arrive_trace_status = partial`
  - `signoff_trace_status = partial`
  - `evidence_count_submitted_only = 1`
  - `evidence_status_submitted_only = partial`
