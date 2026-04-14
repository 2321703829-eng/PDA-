# 2026-04-13 Dashboard Exception Real Data

## Summary

- updated `logistics_web` dashboard summary controller to read real data from `logistics.trace.exception`
- switched dashboard exception-related card clicks to open real exception lists
- switched dashboard priority queue to use real exception records when available

## Files

- `custom_addons/logistics_web/controllers/logistics_web_dashboard.py`
- `custom_addons/logistics_web/static/src/js/actions/dashboard_action.js`

## Details

- `pending_exception_count` now counts exceptions in `open` and `processing`
- `evidence_missing_count` now counts active exceptions with `exception_type = evidence_missing`
- `high_risk_batch_count` now derives from batches linked to high/critical exceptions
- `new_dispute_count` now derives from exceptions reported today
- dashboard priority queue now prefers recent active exception records
- dashboard recent changes now prefers recent exception updates
- exception-related summary cards and drill-down entry now open `logistics.trace.exception`

## Notes

- no module upgrade or runtime verification was executed in this step
- dashboard still retains frontend fallback data if backend records are not yet available
