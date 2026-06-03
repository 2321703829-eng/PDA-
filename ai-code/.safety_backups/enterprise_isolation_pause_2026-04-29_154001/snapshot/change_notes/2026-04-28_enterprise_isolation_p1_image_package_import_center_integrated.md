# 2026-04-28 enterprise_isolation_p1_image_package_import_center_integrated

## What changed

- Connected `image_package` import into the existing `logistics_web` import center.
- Added a new image-package upload section to the import-center client action.
- Added a backend HTTP upload route for image-package ZIP import.
- Added task-opening shortcuts so users can jump from the import center to the created image-package task.
- Added a lightweight image-package result summary area in the import center.

## Files

- `custom_addons/logistics_web/controllers/logistics_web_import_v3.py`
- `custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`

## Behavior

- Users can now choose a ZIP image package directly in the import center.
- Upload uses `/api/admin/logistics/imports/image-package/upload`.
- On success, the page stores the returned task summary, shows a success notification, and opens the current task form.
- The import center also provides a direct button to open the image-package task list.
- Standard waybill import and route-planning import flows remain unchanged.

## Verify

- `node --check custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- XML parse check for `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`
- Upgraded `logistics_web` on `odoo_logistics_dev` with `--stop-after-init`

## Notes

- This slice focuses on integrating the backend image-package capability into the current import-center flow.
- Full browser click-through validation is still recommended with `?debug=assets`, especially for:
  - image-package upload
  - task opening
  - failed-line retry entry visibility
  - linked evidence drill-down
