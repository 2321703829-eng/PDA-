# 2026-05-07 v19 evidence upload_role schema hotfix

## Issue

Refreshing the v19 web page on `http://127.0.0.1:19070` raised an RPC error on model `logistics.trace.evidence`.

Key database error:

- `psycopg2.errors.UndefinedColumn: column logistics_trace_evidence_image.upload_role does not exist`

## Root cause

- The deployed code for `logistics_trace_evidence` defines `logistics.trace.evidence.image.upload_role` as a `store=True` related field.
- On database `odoo_logistics_webtest_v19`, the physical column and `ir_model_fields` metadata for that field were missing.
- This indicates the module code had been updated earlier, but the target v19 database had not yet run the corresponding module upgrade.

## Fix

Executed module upgrade on `192.168.0.17`:

- container: `odoo-lite-test-v19-web`
- database: `odoo_logistics_webtest_v19`
- command: `odoo -c /etc/odoo/odoo.conf -d odoo_logistics_webtest_v19 -u logistics_trace_evidence --stop-after-init`

## Result

- Odoo completed the `logistics_trace_evidence` upgrade successfully.
- Follow-up verification confirmed the `logistics_trace_evidence_image.upload_role` column and corresponding `ir_model_fields` record now exist.
- The reported RPC error should be resolved after page refresh.
