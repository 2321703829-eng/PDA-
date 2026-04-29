# 2026-04-17 Driver Management Mock Mode

## Changes

- Added a local mock mode for the driver management frontend action
- Added a header toggle to enable or disable mock mode
- Added fixed demo data for the list, profile, KPI cards, trends, recent waybills, and recent exceptions
- Added read-only protection in mock mode so real business records are not opened by mistake

## Files

- `custom_addons/logistics_web/__manifest__.py`
- `custom_addons/logistics_web/static/src/js/actions/driver_management_action_v2.js`
- `custom_addons/logistics_web/static/src/xml/driver_management_templates_v2.xml`
- `custom_addons/logistics_web/static/src/scss/driver_management_v2.scss`

## Usage

- Open `Logistics -> Driver Management`
- Click `Enable Mock` in the page header
- Refreshing the page will keep the mock switch state until it is turned off
