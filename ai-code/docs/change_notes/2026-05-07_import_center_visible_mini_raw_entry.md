# 2026-05-07 import center visible entry for mini raw sheet

## Summary

Added a visible web import-center entry for the new mini-program raw sheet import mode, and wired a full admin-side upload flow into the existing import-center page.

## Frontend changes

Updated the web import-center frontend in `logistics_web`:

- added a top-level entry switch card group to the import-center page
- added a dedicated visible card for `?????????`
- added a dedicated web section for:
  - template/info display
  - file upload
  - precheck result summary
  - confirm action
  - import result summary
- kept the existing standard waybill, route-planning, and phase5 sections, and added section anchors for direct entry switching

## Files changed

- `logistics_web/static/src/js/actions/import_center_action.js`
- `logistics_web/static/src/xml/import_center_templates.xml`

## Deployment

Deployed the frontend changes to the actual v19 environment behind the user's tunnel:

- host: `192.168.0.17`
- container: `odoo-lite-test-v19-web`
- database: `odoo_logistics_webtest_v19`

Executed:

- upload updated JS/XML assets
- upgrade module: `logistics_web`
- restart container: `odoo-lite-test-v19-web`

## Expected result

When opening the web import center through the user's actual entry path, the page should now show a clear visible card/option for `?????????`, and the page should include the corresponding upload/precheck/confirm area.
