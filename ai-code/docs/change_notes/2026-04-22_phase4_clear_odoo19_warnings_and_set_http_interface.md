# 2026-04-22 Phase4 Clear Odoo19 Warnings And Set Http Interface

## What Changed

- added `author` to custom addon manifests:
  - `logistics_base`
  - `logistics_dispatch`
  - `logistics_trace_core`
  - `logistics_trace_evidence`
  - `logistics_trace_exception`
  - `logistics_web`
- replaced legacy `_sql_constraints` declarations in `logistics_base` and `logistics_dispatch` models with Odoo 19 `models.Constraint(...)`
- refactored `product.template.product_name` from a stored related field to a standalone synchronized field to avoid the translated related-field warning
- set `http_interface = 127.0.0.1` in `odoo_local.conf` to remove the startup warning about the default HTTP binding

## Verification

- upgraded modules successfully with:
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_base,logistics_dispatch,logistics_web --stop-after-init`
- confirmed the previous three warning classes no longer appear during module upgrade

## Notes

- Odoo still logs `Keep unexpected index product_template__product_name_index on table product_template` as an info message.
- this is an old retained index, not an active warning or upgrade blocker
