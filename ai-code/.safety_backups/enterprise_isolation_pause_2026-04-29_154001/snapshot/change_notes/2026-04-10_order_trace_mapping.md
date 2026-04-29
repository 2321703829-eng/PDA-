# 2026-04-10 order trace mapping

## Summary

Added two new architecture documents to map the mature order, batch, trace, and image domains into Odoo models.

## Added

- docs/architecture/logistics_order_mapping.md
- docs/architecture/logistics_trace_mapping.md
- refreshed docs/architecture/logistics_order_addon_design.md
- refreshed docs/architecture/logistics_trace_addon_design.md

## Key decisions

- shipment_order and shipment_batch are treated as snapshot-layer models
- trace_record and trace_record_image are treated as fact-layer models
- client_id remains as an explicit field in the first-stage Odoo mapping
- customer, store, employee, and warehouse relations stay weakly bound for now
- image binary storage remains outside Odoo; Odoo stores business metadata and image_access_key

## Verification

- document-only changes
- no compilation
- no service startup
- no module upgrade
