# 2026-04-16 dispatch import model text cleanup after recovery

## Summary

- Cleaned mojibake and broken strings in `logistics_dispatch_waybill_customer_line.py`
- Cleaned mojibake and broken strings in `logistics_dispatch_waybill_customer_goods_line.py`
- Synced `*_v2.py` import model files to the same clean Chinese copy
- Cleaned import template labels and validation messages in `logistics_dispatch_import_support.py`
- Reconnected `logistics_dispatch_import_support.py` in `models/__init__.py`
- Rewrote `custom_addons/logistics_web/data/base_import_mapping_data.xml` to a clean Chinese mapping set for wave, batch, waybill, customer line, and goods line import scenarios

## Verify

- Python compile passed for the cleaned import model files
- XML parse passed for `base_import_mapping_data.xml`
- Confirmed key user-facing strings are now readable Chinese

