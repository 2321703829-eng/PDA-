# 2026-04-13 Exception Detail Linkage

## Summary

- enhanced exception detail form to better support trace reading workflow
- added smart-button style object actions from exception to waybill, trace event, and evidence list
- added real evidence count aggregation onto exception model

## Files

- `custom_addons/logistics_trace_exception/models/logistics_trace_exception.py`
- `custom_addons/logistics_trace_exception/views/logistics_trace_exception_views.xml`

## Details

- added computed `evidence_count` on `logistics.trace.exception`
- added `action_open_waybill`
- added `action_open_trace_event`
- added `action_open_evidence`
- exception form now shows button-box entry points for:
  - waybill
  - trace event
  - evidence

## Notes

- no module upgrade or runtime verification was executed in this step
- these actions will be validated after PostgreSQL environment is ready and module upgrades are rerun
