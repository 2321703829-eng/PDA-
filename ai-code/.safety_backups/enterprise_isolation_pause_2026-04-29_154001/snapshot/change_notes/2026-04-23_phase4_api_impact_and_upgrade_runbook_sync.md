# 2026-04-23 Phase4 API Impact And Upgrade Runbook Sync

## Objective

Sync the phase-4 first-round scope reduction into:

- backend API impact documentation
- request / response DTO wording
- executable database / module upgrade runbook

## Main Updates

### 1. API impact doc

Updated:

- `前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期后端数据库与接口影响面调研稿.md`

Key sync points:

- clarified first-round scope keeps only driver and vehicle profiles
- marked dispatch state / assignment history / state change log as deferred
- updated product-unit DTO to one-row-per-sales-unit
- updated address DTO to `address_full + longitude + latitude + address_region_json`
- removed `has_own_vehicle` from driver list request parameters
- clarified driver / vehicle runtime status now derives from active batch instead of dispatch-state tables

### 2. Upgrade docs

Added:

- `docs/dev/phase4_first_round_scope_alignment_upgrade_runbook.md`

Updated:

- `docs/dev/upgrade_and_verify.md`

Key sync points:

- added a dedicated runbook for this phase-4 scope alignment
- provided a recommended clean-path upgrade strategy based on rebuilding a new dev database
- also documented an in-place upgrade fallback path
- listed old tables and old product-unit columns that may need manual cleanup in reused dev databases

## Notes

- This change is documentation-only.
- No runtime code was modified in this sync step.
