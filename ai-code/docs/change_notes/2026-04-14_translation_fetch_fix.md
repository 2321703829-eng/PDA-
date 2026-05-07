# 2026-04-14 Translation Fetch Fix

## Objective

Fix the Odoo web translation fetch failure for custom logistics addons under `zh_CN`, and make the logistics frontend compatible with Odoo language switching.

## Root Cause

The custom addon translation files were previously hand-written and did not follow the canonical Odoo PO export structure required by the webclient translation loader.

The backend route:

- `/web/webclient/translations?lang=zh_CN`

started failing when custom logistics modules were included, because Odoo expected PO entry metadata such as:

- `#. module: ...`
- `#. odoo-javascript`
- `#. odoo-python`
- `#: code:addons/...`

The previous files contained mostly direct `msgid/msgstr` entries without the expected metadata, which caused the web translation reader to crash.

## Changes

- Backed up the previous custom translation files as `zh_CN.before_reexport.po`
- Re-exported canonical `zh_CN.po` files for:
  - `logistics_dispatch`
  - `logistics_trace_core`
  - `logistics_trace_evidence`
  - `logistics_trace_exception`
  - `logistics_web`
- Merged the previous translation content back into the exported skeletons by `msgid`
- Revalidated the backend translation route

## Verification

Confirmed that the translation endpoint now responds successfully:

- `/web/webclient/translations?lang=zh_CN` -> `200 OK`

Confirmed that the previous failure is no longer reproduced at the backend route level.

## Notes

After this change, the running Odoo instance still needs:

1. module upgrade
2. service restart
3. browser hard refresh or cleared cached assets

before the frontend fully reflects the fixed translation state.
