# 2026-04-24 from_waybill export controller first round landed

## This round

- Land `WB-EXP-C1` for the first `from_waybill` export slice.
- Expose the already-landed export service through formal admin routes under `/api/admin/logistics/exports/...`.

## Changed files

- `custom_addons/logistics_web/controllers/logistics_web_export.py`
- `custom_addons/logistics_web/controllers/__init__.py`

## What changed

- Add a new export controller `LogisticsWebExportController`.
- Wire the first-round formal routes:
  - `POST /api/admin/logistics/exports/waybill`
  - `GET /api/admin/logistics/exports/tasks/<task_no>`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/lines`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/errors`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/error-report`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/download`
- Keep the response shell aligned with the current import controller style:
  - top-level `code / message / data / request_id`
  - download routes return file bytes directly
- Make the `POST /exports/waybill` route synchronously call:
  - `create_waybill_export_task`
  - `run_waybill_export_task`
  so the first-round slice can complete without adding a separate run route.
- Add request payload helpers for:
  - JSON body merge
  - `selected_ids` string/list normalization
  - `scope_snapshot` JSON string parsing
- Preserve service-layer export error codes where available instead of collapsing all failures into one generic controller code.

## Boundary

- This round only exposes `from_waybill`.
- `from_batch` and `from_customer` routes are not added yet.
- This round does not add frontend result-page routing or list/detail entry buttons yet.

## Verify

- Parse [logistics_web_export.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/logistics_web_export.py:1) with Python `ast.parse`.
- Confirm controller registration in [controllers/__init__.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/__init__.py:1).

## Risks

- The create route currently executes synchronously in the controller path; if later export volume becomes large, this should be upgraded to async worker execution without changing the task readback routes.
- This round still lacks real HTTP smoke against a running Odoo instance.

## Next

- Continue with frontend result page and action wiring so list/detail page export can jump into the task result flow directly.
