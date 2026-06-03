# 2026-04-13 Boss Trace Real Data

## Summary

- updated `Boss Trace Overview` to read real dispute and high-risk aggregation data
- switched boss trace cards to use real `logistics.trace.exception` counts
- implemented focus object list based on active exceptions

## Files

- `custom_addons/logistics_web/controllers/logistics_web_dashboard.py`
- `custom_addons/logistics_web/static/src/js/actions/boss_trace_action.js`
- `custom_addons/logistics_web/static/src/xml/dashboard_templates.xml`
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

## Details

- `boss_trace_summary` now returns:
  - `open_disputes`
  - `high_risk_batches`
  - `critical_disputes`
  - `evidence_missing`
  - `today_new`
- boss trace focus objects now prefer active exception records
- boss trace cards now drill down to real exception or batch lists
- boss trace page now renders headline cards and focus object cards instead of placeholder text

## Notes

- no module upgrade or runtime verification was executed in this step
- frontend still keeps placeholder fallback data if backend aggregation is unavailable
