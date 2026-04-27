# 2026-04-11-005 Add Real Service Validation And Image Reference Views

## Summary

This round pushes `feat-image-4a` closer to real integration acceptance instead of staying at scaffold level.

## What Changed

- Added a real image-service connectivity check in Odoo settings.
- Added `/api/images` list support in the Odoo image client so the module can validate the external service without mock data.
- Added `Evidence Images` list/form/search views for direct inspection of image references inside Odoo.
- Added direct preview and download actions that open the independent image service URLs instead of relying on Odoo binary storage.
- Updated collaboration and acceptance docs to emphasize:
  - image association is based on batch number or waybill number
  - image binaries stay in the external image service
  - feasibility validation must use a real image-manager service, not mock-only confirmation

## Why

The feature owner needs to validate feasibility later with real uploads and real metadata. A mock-only path would not be enough for team acceptance.

## Impact

- Better alignment with `image-manager-main`
- Easier real-service validation during joint integration
- Clearer separation between Odoo business records and external image storage
