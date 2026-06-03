# 2026-04-29 odoo_logistics_dev Fixed Entry Verified And Docs Synced

## Background

The dedicated runtime config for `odoo_logistics_dev` had already been prepared, but it still needed a verified local entry and synced delivery docs.

## What changed

- started the dedicated fixed-entry instance for `odoo_logistics_dev`
- verified the following URLs return the login page:
  - `http://127.0.0.1:8071/web/login`
  - `http://localhost:8071/web/login`
- verified `/web/database/selector` redirects back to `/web/login` on port `8071`
- synced the local entry split into the `P0` environment register and the final delivery note

## Practical result

The local environment now has a clearer split:

- `8069` -> original multi-db gateway
- `8070` -> `tenant_kebi`
- `8071` -> `odoo_logistics_dev`
