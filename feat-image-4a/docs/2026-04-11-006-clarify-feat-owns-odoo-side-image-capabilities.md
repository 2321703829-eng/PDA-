# 2026-04-11-006 Clarify Feat Owns Odoo Side Image Capabilities

## Summary

Refined the feature-line positioning after alignment: `feat-image-4a` itself must carry the Odoo-side implementation for evidence-image capabilities. The external image service is only the binary and metadata storage backend.

## What Changed

- Clarified in docs that `feat-image-4a` is not only an adapter layer.
- Explicitly stated that the feature folder must contain Odoo-side code for:
  - image upload actions
  - image reference management
  - metadata synchronization
  - preview/download entry points
  - business constraints based on batch number or waybill number
- Fixed a missing `UserError` import in the evidence image model so preview/download actions remain valid Odoo code.

## Why

The final team integration will run on top of Odoo. Each `feat` folder must therefore provide real Odoo functionality, not just external-service connection notes.
