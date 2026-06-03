# 2026-04-30 phase5 import export delivery

## What changed

- added phase-5 workbook import object type and import routes
- added phase-5 workbook import service
- added direct export routes for the three `0429` workbooks
- added phase-5 import and export sections to the import center frontend
- added phase-5 related fields for product units, order lines, and goods lines
- exposed the new phase-5 fields in waybill related views

## Why

- the phase-5 scope requires five workbook imports to be runnable in Odoo
- the phase-5 scope requires the three `0429` workbooks to be exportable from Odoo
- the frontend needed a visible entry so test and business users can operate without backend assistance

## Result

- the system now supports phase-5 workbook template download, precheck, and confirm import
- the system now supports direct export for the three `0429` workbook formats
- the import center now includes phase-5 upload, validation, import result, and export UI
- the database model now carries the phase-5 fields needed for display and export
