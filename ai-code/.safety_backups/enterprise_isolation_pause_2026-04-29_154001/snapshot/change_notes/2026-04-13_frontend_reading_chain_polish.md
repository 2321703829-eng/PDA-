# 2026-04-13 Frontend Reading Chain Polish

## Summary

- enhanced exception list/detail readability and linkage
- completed more direct cross-navigation between waybill trace, evidence, and exception contexts
- unified dashboard and boss trace action naming toward `Open ...`
- added clearer empty states for dashboard and boss trace pages

## Files

- `custom_addons/logistics_trace_exception/models/logistics_trace_exception.py`
- `custom_addons/logistics_trace_exception/views/logistics_trace_exception_views.xml`
- `custom_addons/logistics_web/static/src/js/views/logistics_waybill_form_view.js`
- `custom_addons/logistics_web/static/src/js/widgets/evidence_viewer_widget.js`
- `custom_addons/logistics_web/static/src/xml/widget_templates.xml`
- `custom_addons/logistics_web/static/src/js/actions/dashboard_action.js`
- `custom_addons/logistics_web/static/src/js/actions/boss_trace_action.js`
- `custom_addons/logistics_web/static/src/xml/dashboard_templates.xml`
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

## Details

- exception form now supports direct open actions for:
  - waybill
  - batch
  - trace event
  - evidence
- exception list now shows stronger visual cues for severity and overdue state
- evidence viewer now supports opening related exceptions
- timeline exception label now prefers real open exception counts when available
- dashboard and boss trace pages now show explicit empty states
- action/button/window naming was aligned toward `Open ...`

## Notes

- no module upgrade or runtime verification was executed in this step
- these changes should be validated together with the first full module load after PostgreSQL is ready
