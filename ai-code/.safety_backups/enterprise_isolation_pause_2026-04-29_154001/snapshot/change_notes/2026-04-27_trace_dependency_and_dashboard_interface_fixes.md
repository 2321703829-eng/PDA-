# 2026-04-27 Trace Dependency And Dashboard Interface Fixes

## Objective

Resolve the `logistics_trace_evidence` dependency inconsistency and tighten the trace dashboard interface contract.

## What Changed

- Reworked `logistics.trace.evidence.is_exception_related` to depend on core event type instead of `logistics_trace_exception` extension fields.
- Added UTC-safe local-day window calculation for dashboard "today" metrics.
- Added top-level `5000 / ANALYSIS_INTERNAL_ERROR` JSON fallback to the dashboard controller.
- Added a dedicated review report for this round.

## Verify Plan

- Parse touched Python files.
- Upgrade `logistics_trace_evidence` and `logistics_web`.
- Run dashboard shell smoke for summary payloads and forced controller fallback.

## Verify Result

- Python AST parse passed for:
  - `logistics_trace_evidence/models/logistics_trace_evidence.py`
  - `logistics_web/models/logistics_dashboard_service.py`
  - `logistics_web/controllers/logistics_web_dashboard.py`
- Module upgrade passed on `odoo_logistics_phase4_v1`:
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_trace_evidence,logistics_web --stop-after-init`
- Dashboard shell smoke passed:
  - summary payload structure returned normally
  - boss trace payload structure returned normally
  - forced controller fallback returned `5000 / ANALYSIS_INTERNAL_ERROR`
- Dependency smoke passed:
  - seeded `exception_report` trace event `id = 3`
  - evidence created from that event computed `is_exception_related = True`
