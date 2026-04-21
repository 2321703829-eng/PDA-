# 2026-04-17 logistics_web action self-registration fix

## What changed

- moved logistics frontend action registration from a centralized registry module
  into each individual action module
- kept `logistics_action_registry.js` as a lightweight import entrypoint so the
  backend asset bundle still executes each action module
- fixed `driver_management_action_v2.js` registration order so the action is
  registered only after `LogisticsDriverManagementActionV2` is defined

## Why

- previous runtime behavior allowed one broken import in the centralized
  registration chain to remove multiple actions from the Odoo `actions`
  registry
- the reported error was:
  - `Cannot find key "logistics_web.home" in the "actions" registry`
- self-registration reduces blast radius so a failure in one action module does
  not silently unhook unrelated entries like `logistics_web.home`
- Odoo backend assets still need an import chain for those modules to execute,
  so the registry file now imports action modules without re-owning the full
  registration logic
- the browser white-screen root cause was a frontend `ReferenceError`:
  `Cannot access 'LogisticsDriverManagementActionV2' before initialization`

## Affected files

- `custom_addons/logistics_web/static/src/js/actions/home_action.js`
- `custom_addons/logistics_web/static/src/js/actions/dashboard_action_v2.js`
- `custom_addons/logistics_web/static/src/js/actions/boss_trace_action_v2.js`
- `custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- `custom_addons/logistics_web/static/src/js/actions/driver_management_action_v2.js`
- `custom_addons/logistics_web/static/src/js/actions/stats_center_action.js`
- `custom_addons/logistics_web/static/src/js/actions/logistics_action_registry.js`

## Verify

- `node --check` passed for all updated action modules
- `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_web --stop-after-init`
  passed
