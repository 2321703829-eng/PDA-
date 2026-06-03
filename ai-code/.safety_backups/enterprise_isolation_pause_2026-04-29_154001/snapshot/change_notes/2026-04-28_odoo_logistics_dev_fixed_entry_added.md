# 2026-04-28 odoo_logistics_dev Fixed Entry Added

## Background

After `tenant_kebi` received its own fixed local entry on port `8070`, the original development entry on `8069` still behaved like a multi-database gateway.

This made it inconvenient to switch cleanly between:

- `tenant_kebi`
- the original main development database

## What changed

Added a dedicated fixed-entry runtime config for the original main development database:

- file: `.runtime/odoo_dev_fixed.conf`

Current fixed-entry rule:

- port: `8071`
- database filter: `^odoo_logistics_dev$`
- database list: closed

## Practical result

The workspace now has clearer local entry separation:

- `8069`: original multi-db development gateway behavior remains
- `8070`: fixed entry for `tenant_kebi`
- `8071`: fixed entry for `odoo_logistics_dev`

## Purpose

- make manual switching between validation tenant and main dev database easier
- avoid relying on session memory when returning to the original development database
