# 2026-04-28 enterprise isolation `P1` trace/evidence/exception/dispatch first code slice

## Summary

Implemented the first coding slice for the current enterprise-isolation `P1` design across:

- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`
- `logistics_dispatch` linkage by inherited waybill summaries and entry actions

## What changed

### 1. Trace core

- Added lightweight tenant-internal role groups:
  - `group_logistics_readonly_viewer`
  - `group_logistics_dispatch_operator`
  - `group_logistics_image_field_operator`
- Tightened `logistics.trace.event` access:
  - `base.group_user` is no longer allowed to create trace events directly
  - create access is granted to dispatch operator / image field operator / trace manager groups
- Added explicit access reuse for:
  - `base.group_system`
  - `logistics_dispatch.group_logistics_dispatch_manager`
- Added model-level trace submit permission guard
- Extended `waybill` trace summary with:
  - `latest_trace_user_id`
  - `has_exception_related_trace`
- Synced core trace list/form/search/action/button labels back to Chinese

### 2. Evidence

- Added evidence-side matching and linking fields:
  - `matched_waybill_id`
  - `matched_customer_line_id`
  - `match_status`
  - `match_remark`
  - `link_status`
  - `linked_at`
  - `linked_by`
- Added default evidence link normalization from `trace_event -> waybill`
- Extended `waybill` evidence summary with:
  - `latest_evidence_time`
  - `latest_image_access_key`
- Added `waybill` evidence list entry action
- Added evidence form/list/search support for match and link fields
- Added `group_logistics_image_auditor`
- Tightened evidence access from broad `base.group_user create` to role-based create / write
- Added explicit access/rule reuse for:
  - `base.group_system`
  - `logistics_dispatch.group_logistics_dispatch_manager`
- Synced evidence list/form/search/action/button labels and key field labels back to Chinese

### 3. Exception

- Added `group_logistics_exception_handler`
- Tightened exception access from broad `base.group_user create` to role-based create / write
- Added explicit access/rule reuse for:
  - `base.group_system`
  - `logistics_dispatch.group_logistics_dispatch_manager`
- Added model-level state-change / close-summary / process-owner handling guard
- Extended `waybill` exception summary with:
  - `latest_exception_time`
  - `latest_exception_type`
  - `highest_exception_status`
  - `has_processing_exception`
- Opened exception action buttons to handler / trace manager / dispatch manager groups
- Synced exception list/form/search/action/button labels back to Chinese

## Verification

- Python source compile check passed for all modified model files
- XML parse check passed for all modified security and view files
- Runtime module upgrade path executed on `odoo_logistics_dev`
  - initial `logistics_trace_core` upgrade exposed an outdated database baseline: missing `res_partner.is_logistics_partner`
  - resolved by upgrading `logistics_base,logistics_dispatch` first
  - then reran ordered upgrades for:
    - `logistics_trace_core`
    - `logistics_trace_evidence`
    - `logistics_trace_exception`
- Fixed one runtime-discovered ACL data issue:
  - duplicate XML ID in `logistics_trace_evidence/security/ir.model.access.csv`
- Odoo shell regression checks confirmed:
  - new tenant-internal groups are present
  - new `waybill` summary fields are available
  - effective merged `waybill` form contains:
    - `action_open_trace_events`
    - `action_open_evidences`
    - `action_open_exceptions`
    - `latest_evidence_time`
    - `highest_exception_status`
    - `js_class="logistics_waybill_form"`
- After the first manual feedback round:
  - confirmed the visible English `Trace / Evidence / Open Exceptions / Match Status / Link Status` text was a label-sync problem, not a failed model upgrade
  - confirmed current `admin` user originally had `base.group_system` only and none of the newly added lightweight groups
  - added direct create/read access reuse so `base.group_system` and dispatch manager users can work without extra manual role assignment
  - verified by shell that `admin` can now create:
    - `logistics.trace.event`
    - `logistics.trace.evidence`
    - `logistics.trace.exception`
  - executed a temporary waybill trace-and-evidence create flow under savepoint rollback, confirming:
    - trace create succeeds
    - evidence create succeeds
    - evidence defaults fill `waybill_id`
    - evidence defaults fill `match_status=matched`
    - evidence defaults fill `link_status=linked`
  - found one additional runtime UX gap in exception handling:
    - draft exceptions had no visible page action to move into `open`
    - model transitions already allowed `draft -> open` and `draft -> cancelled`
    - added `action_mark_open` and `action_mark_cancelled`
    - added header buttons so draft exceptions can now enter the handling flow from the UI

## Notes

- This is the first implementation slice aimed at supporting `P1` linkage and regression, not the final full isolation platform build
- No `P2/P3` platform-side tenant master / subscription / control-plane models were introduced in this slice
- Evidence create still formally anchors to `trace_event_id`; operationally this means:
  - users should create trace first
  - then create evidence under that trace / waybill context
