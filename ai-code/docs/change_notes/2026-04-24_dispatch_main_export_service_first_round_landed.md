# 2026-04-24 from_waybill export service first round landed

## This round

- Land `WB-EXP-S1` for the first real `from_waybill` export slice.
- Add a reusable service entry in `logistics_web/services` so the next controller work can call a stable service layer instead of mixing task logic into routes.

## Changed files

- `custom_addons/logistics_web/services/dispatch_main_export_service.py`
- `custom_addons/logistics_web/services/__init__.py`

## What changed

- Add `DispatchMainExportService` and `ExportServiceError`.
- Freeze the first service-layer contract around:
  - `create_waybill_export_task`
  - `run_waybill_export_task`
  - `get_export_task_result`
  - `get_export_task_lines`
  - `get_export_task_errors`
  - `build_export_task_error_report`
  - `get_export_download_file`
- Reuse the formal four-sheet field contract from `waybill_standard_import_service_v2` so export output stays aligned with the current import template.
- Implement the first synchronous `from_waybill` export flow:
  - validate scope and source waybill readability
  - create `export_source_scope` and `export_task`
  - create `export_task_line`
  - collect waybill/customer/order/goods rows
  - build workbook bytes
  - store output file under `.odoo_data/export_tasks/...`
  - write task summary, counters, file metadata, and error lines
- Implement first-round task readback payloads for summary, line list, error list, error report, and output file download.

## Boundary

- This round only covers `dispatch_main + from_waybill + standard_xlsx + dispatch_main_four_sheet`.
- This round does not add controller routes, frontend result page wiring, or list/detail entry buttons yet.
- This round keeps execution synchronous inside the service to get the minimal export chain working first.

## Verify

- Parse [dispatch_main_export_service.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/dispatch_main_export_service.py:1) with Python `ast.parse`.
- Confirm service module registration in [services/__init__.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/__init__.py:1).

## Risks

- The current export sheet mapping is intentionally first-round and focuses on the fields already available in `logistics_dispatch`; some template columns are exported as blanks until later data enrichment lands.
- The service has not yet been exercised through a real Odoo HTTP route or module upgrade in this round.

## Next

- Continue with `WB-EXP-C1` to expose task create/result/error/download routes in `logistics_web/controllers`.
