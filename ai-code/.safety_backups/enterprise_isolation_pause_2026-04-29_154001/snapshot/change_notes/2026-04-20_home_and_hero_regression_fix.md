# 2026-04-20 Homepage And Hero Regression Fix

## Objective

Repair the visual regressions introduced during the shared hero/state cleanup:

- homepage hero copy block rendered incorrectly
- hero subtitle text was repainted with normal body copy color
- page heroes lost stable radius, padding, and spacing on several phase-3 pages

## Changes

- Repaired the malformed hero note node in `custom_addons/logistics_web/static/src/xml/home_action_templates.xml`.
- Narrowed the shared `page_header p` copy rule in `custom_addons/logistics_web/static/src/scss/logistics_web.scss` to non-hero headers only.
- Added a final shared hero box-model override in `custom_addons/logistics_web/static/src/scss/logistics_web.scss` to stabilize:
  - radius
  - padding
  - gap
  - margin-bottom
  - responsive single-column fallback
- Strengthened homepage brandline text contrast so the system name no longer looks washed out inside the hero.

## Impact

Affected pages:

- homepage
- stats center
- logistics dashboard
- import center
- import result page
- driver management
- boss trace board

## Verify

- `python ai-code/scripts/check_odoo_frontend_assets.py custom_addons/logistics_web`
  - `Errors: 0`
  - `Warnings: 0`
- XML parse passed for:
  - `custom_addons/logistics_web/static/src/xml/home_action_templates.xml`
