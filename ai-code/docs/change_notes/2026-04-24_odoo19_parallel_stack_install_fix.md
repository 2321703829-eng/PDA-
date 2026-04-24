# 2026-04-24 Odoo 19 Parallel Stack Install Fix

## Objective

Fix the Odoo 19 installation blocker for the latest logistics modules on the parallel server stack.

## What Changed

- Removed the direct `logistics_web.action_logistics_web_dashboard` binding from
  `logistics_dispatch.menu_logistics_dispatch` in
  `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`.
- Removed the stale `menu_logistics_dispatch_enterprise_home` update record from
  `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml` because
  that menu is not defined during a fresh install.

## Why

- `logistics_dispatch` was referencing a client action defined by `logistics_web`
  during its own XML data load.
- `logistics_web` already depends on `logistics_dispatch`, so this created an
  install-time cross-module ordering issue on a fresh Odoo 19 database.
- The existing `logistics_web` menu sync logic already writes the dashboard
  action back onto that menu after both modules are installed, so the direct XML
  dependency was unnecessary.
- A historical menu toggle record was also being loaded for an XML ID that does
  not exist in a clean database, which broke fresh installs even after the menu
  action dependency was removed.

## Result

- `logistics_dispatch` can now install independently on a fresh Odoo 19
  database.
- `logistics_web` remains responsible for enhancing the logistics menu into the
  dashboard entry after installation.
