# 2026-05-07 mini raw-sheet customer seed import from template V1

## Summary

To make the mini-program raw-sheet import testable on the v19 environment behind `127.0.0.1:19070`, customer master data was seeded from `???????V1.xlsx` and one normalization edge case in the mini raw-sheet import service was fixed.

## Data import

Source workbook:

- `D:\Desktop\???????V1.xlsx`

Seed strategy:

- imported customer master rows from `??????`
- overlaid current-batch geo/address/phone data from `template`
- wrote data into `res.partner` and created missing `logistics.store.profile` records

Observed import result on `odoo_logistics_webtest_v19`:

- created partner records: `2`
- updated partner records: `1109`
- overlay-updated partner records: `8`
- created store-profile records: `8`

## Matching completion work

Two remaining mini raw-sheet mismatches were then handled as follows:

- fixed `_normalize_text()` in `logistics_web/services/mini_program_raw_sheet_import_service.py` to remove whitespace around parentheses so merged-line breaks no longer block exact-name matching
- created one exact customer master record for:
  - `?????????????? 10?`

## Verification

Re-ran mini raw-sheet precheck using:

- `D:\Desktop\????????.xlsx`

Final verified task:

- `task_no = IMT260507-00014`
- `deduplicated_row_count = 13`
- `matched_row_count = 13`
- `unmatched_row_count = 0`
- `can_confirm_import = true`

This confirms the current v19 environment now has enough customer master data for the provided raw workbook to pass precheck.
