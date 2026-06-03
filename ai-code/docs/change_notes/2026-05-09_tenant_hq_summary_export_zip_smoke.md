## 2026-05-09 tenant_hq summary export zip smoke

### Background

- Goal: add one minimal readable evidence record in `tenant_hq` and run the summary-image export chain through to a real zip artifact on `19109`.
- Environment:
  - container: `enterprise-multidb-odoo19`
  - database: `tenant_hq`
  - port: `19109`

### Data seeded

- Selected waybill:
  - `waybill_id = 468`
  - `waybill_no = YD2026040200138`
- Created trace event:
  - `trace_event_id = 103`
- Created evidence:
  - `evidence_id = 184`
  - `upload_role = warehouse`
  - `name = SUMMARY EXPORT SMOKE 20260509`
- Generated summary row:
  - `summary_id = 184`

### Export result

- Export task:
  - `task_no = EXT260509-00012`
  - `status = success`
- Output file:
  - `output_file_name = TSL-EXPORT-EVIDENCE-IMAGE-20260509-020040.zip`
  - `output_storage_path = 2026/05/09/EXT260509-00012/TSL-EXPORT-EVIDENCE-IMAGE-20260509-020040.zip`
  - `output_file_size = 1211`
- Download ready:
  - `true`
- Download URL:
  - `/api/admin/logistics/exports/tasks/EXT260509-00012/download`

### Zip entries

- `YD2026040200138/warehouse/evidence_184/001_summary-export-smoke-20260509.png`
- `index.csv`
- `manifest.json`

### Conclusion

- `tenant_hq` now has a minimal readable evidence-summary test sample.
- The latest `feat-text` evidence summary export chain on `19109` has been driven to a real zip artifact successfully.
- This closes the previous regression gap where summary export code was deployed but no readable image-backed sample existed in `tenant_hq`.
