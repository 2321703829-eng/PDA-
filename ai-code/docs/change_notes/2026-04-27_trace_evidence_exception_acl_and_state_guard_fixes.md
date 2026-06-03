# 2026-04-27 Trace Evidence / Exception ACL And State Guard Fixes

## Objective

Close the high-risk permission and audit gaps in `logistics_trace_evidence` and `logistics_trace_exception`.

## What Changed

- Added `group_logistics_trace_manager` in `logistics_trace_evidence`.
- Tightened ACL for `logistics.trace.evidence`, `logistics.trace.exception`, and `logistics.trace.exception.process.log`.
- Added owner-read and manager-read record rules for evidence, exception, and process logs.
- Restricted exception state transition buttons to the trace manager group in the backend form view.
- Added backend exception state-machine validation and mandatory `close_summary` for final states.
- Made exception process logs system-generated and read-only for normal users.
- Forced exception audit log creation through `sudo()` so the audit trail still records manager actions.

## Verify Plan

- Parse touched Python files and XML files.
- Upgrade `logistics_trace_evidence` and `logistics_trace_exception`.
- Run a minimal shell smoke for:
  - owner read vs non-owner read
  - manager transition allowed
  - invalid transition blocked
  - final-state without `close_summary` blocked
  - manual process-log create/write/unlink blocked

## Verify Result

- Python AST parse passed for the two rewritten exception model files.
- XML parse passed for the two new security files and the rewritten exception view.
- ACL CSV structure check passed for evidence and exception modules.
- Module upgrade passed on `odoo_logistics_phase4_v1`:
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_trace_evidence,logistics_trace_exception --stop-after-init`
- Minimal shell smoke passed:
  - owner exception visible: `1`
  - non-owner exception visible: `0`
  - owner evidence visible: `1`
  - non-owner evidence visible: `0`
  - owner process log visible: `1`
  - non-owner process log visible: `0`
  - manager transition result: `processing`
  - invalid transition blocked: `open -> closed`
  - close without `close_summary` blocked
  - manual process-log `create / write / unlink` blocked
