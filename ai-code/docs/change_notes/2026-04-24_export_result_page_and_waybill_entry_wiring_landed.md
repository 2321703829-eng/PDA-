# 2026-04-24 export result page and waybill entry wiring landed

## This round

- Continue after `WB-EXP-S1` and `WB-EXP-C1`.
- Land the first front-end result page and the first user entry buttons so `from_waybill` can go from list/detail page directly into the `task_no` result chain.

## Changed files

- `custom_addons/logistics_web/static/src/js/actions/export_result_action.js`
- `custom_addons/logistics_web/static/src/xml/export_result_templates.xml`
- `custom_addons/logistics_web/static/src/js/actions/logistics_action_registry.js`
- `custom_addons/logistics_web/static/src/js/components/list_import_button.js`
- `custom_addons/logistics_web/static/src/xml/list_import_button.xml`
- `custom_addons/logistics_web/models/logistics_dispatch_waybill.py`
- `custom_addons/logistics_web/views/logistics_web_waybill_views.xml`
- `custom_addons/logistics_web/views/logistics_web_actions.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`
- `custom_addons/logistics_web/__manifest__.py`

## What changed

- Add `logistics_web.export_result` client action.
- Add first export result page that reads:
  - `/api/admin/logistics/exports/tasks/<task_no>`
  - `/lines`
  - `/errors`
  - `/download`
  - `/error-report`
- Reuse the existing import-result page shell and styles so export result can land quickly without creating a second completely different task UI.
- Add a waybill list-page export button:
  - only for `logistics.dispatch.waybill`
  - sends selected ids to `POST /api/admin/logistics/exports/waybill`
  - opens the export result page with returned `task_no`
- Add a waybill form-page export button:
  - object method `action_open_export_result`
  - synchronously creates and runs first-round export
  - returns `ir.actions.client` to open the export result page
- Add formal client action metadata:
  - `logistics_web.action_logistics_web_export_result`
  - UI label sync entry
- Register new frontend assets in the backend bundle.

## Boundary

- This round only wires `from_waybill`.
- It does not add `from_batch` or `from_customer` frontend entry buttons yet.
- It does not add async job execution; form/list entry still uses the first-round synchronous export chain.

## Verify

- Parse changed Python files with `ast.parse`.
- Confirm action registration, client tag registration, and route references are present.
- Manual HTTP/browser smoke is still pending.

## Risks

- The list-page button currently exports the selected ids returned by the list model; very large selection/domain-based export still needs dedicated UX and async handling later.
- The form-page button executes synchronously, so if export volume grows, this path should eventually switch to async task submission while still landing on the same result page.

## Next

- If we keep pushing the same slice, the next natural step is a real browser smoke:
  - list page select waybills -> click export
  - detail page click export
  - verify result page, file download, and error-report download end to end
