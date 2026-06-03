# 2026-04-14 Frontend I18n And Real Dashboard Data

## Objective

1. Replace remaining English-facing menu and frontend action entry labels with Chinese-first labels for the logistics customer-facing backend.
2. Switch `Management Dashboard` and `Boss Trace Overview` from placeholder fallback data to real aggregation reads based on current Odoo models.

## Scope

Updated:

- `custom_addons/logistics_web/views/logistics_web_menus.xml`
- `custom_addons/logistics_web/views/logistics_web_actions.xml`
- `custom_addons/logistics_web/static/src/js/actions/dashboard_action.js`
- `custom_addons/logistics_web/static/src/js/actions/boss_trace_action.js`
- `custom_addons/logistics_web/static/src/xml/dashboard_templates.xml`

## Main Changes

### Chinese-first menu and action labels

- `Frontend` -> `前端`
- `Management Dashboard` -> `管理工作台`
- `Boss Trace Overview` -> `老板追溯总览`

### Dashboard real data

`Management Dashboard` no longer depends on placeholder card arrays as the default browsing state.

It now reads real data through the Odoo ORM service from:

- `logistics.trace.exception`

It computes:

- pending exceptions
- evidence missing exceptions
- high risk batches
- new disputes today
- priority queue
- recent changes

### Boss overview real data

`Boss Trace Overview` now reads real data through the Odoo ORM service from:

- `logistics.trace.exception`

It computes:

- open disputes
- high risk batches
- critical disputes
- evidence missing
- new today
- dispute focus objects

### Template text moved toward runtime UI labels

The dashboard and boss overview template headings and helper texts were switched from fixed inline strings to `this.ui.*` runtime labels so they can align better with frontend translation flow.

## Expected Result

After upgrading `logistics_web` and restarting Odoo:

- top-level logistics frontend entry becomes Chinese
- dashboard and boss overview should load real current data instead of static placeholder cards
- only true load failures should show an error strip

