# 2026-04-13 Boss Trace Three-Level Drilldown

## Summary

- refined `Boss Trace Overview` focus objects to support three-level drilldown
- added direct navigation from boss focus cards to:
  - exception form
  - waybill form
  - batch form

## Files

- `custom_addons/logistics_web/controllers/logistics_web_dashboard.py`
- `custom_addons/logistics_web/static/src/js/actions/boss_trace_action.js`
- `custom_addons/logistics_web/static/src/xml/dashboard_templates.xml`
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

## Details

- boss trace focus objects now expose:
  - `exception_id`
  - `waybill_id`
  - `batch_id`
- clicking a focus card still defaults to exception-level reading
- focus card action buttons now allow explicit drilldown to:
  - current exception
  - related waybill
  - related batch

## Notes

- no module upgrade or runtime verification was executed in this step
- these drilldown actions will be verified after PostgreSQL is ready and module upgrade is rerun
