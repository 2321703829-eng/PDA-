# 2026-04-13 Exception Queue And Test Data Draft

## Summary

- refined exception list default experience toward a processing-queue style entry
- added first-page-validation test data draft for manual verification after environment setup

## Files

- `custom_addons/logistics_trace_exception/views/logistics_trace_exception_views.xml`
- `ai-code/docs/dev/首次页面验证测试数据草案.md`

## Details

- exception action name updated to `Exception Queue`
- exception menu entry updated to `Exception Queue`
- exception action now defaults to `search_default_active`
- exception list now sets a queue-style default order
- exception action now includes an empty-state help message
- added a minimal test-data draft covering:
  - wave
  - batch
  - waybill
  - trace event
  - evidence
  - exception

## Notes

- no module upgrade or runtime verification was executed in this step
- the test data draft is intended for the first manual page check after PostgreSQL is ready
