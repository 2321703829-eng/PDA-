# 2026-04-14 Trace & Evidence Widget Layout Fix

## Objective

Move the waybill `Trace & Evidence` enhanced area away from Odoo field-container rendering so timeline and evidence widgets can render as full-width page blocks.

## Changes

- Replaced field-widget placement in [logistics_web_waybill_views.xml](d:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_waybill_views.xml) with independent host blocks:
  - `o_logistics_waybill_timeline_host`
  - `o_logistics_waybill_evidence_host`
- Kept fallback trace/evidence one2many lists as secondary debug content below the enhanced area.
- Added dedicated host/block styles in [logistics_web.scss](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/scss/logistics_web.scss) so mounted widgets render as full-width notebook content instead of participating in form field layout.
- Fixed a malformed closing structure in [widget_templates.xml](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/xml/widget_templates.xml) inside the evidence thumbnail strip, which could surface as a backend asset/javascript module loading error.
- Simplified both widget layouts to a more conservative single-column structure in [widget_templates.xml](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/xml/widget_templates.xml) and [logistics_web.scss](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/scss/logistics_web.scss):
  - trace items now render as stacked blocks instead of compact two-column cards
  - evidence viewer no longer uses stage/sidebar side-by-side layout in the waybill form context

## Reason

The widget data chain and mounting logic were already working, but field-based rendering kept the components inside Odoo form field containers, causing narrow and overlapping layouts. This change routes rendering through independent page-level hosts.

## Verify

After upgrading `logistics_web` and restarting Odoo:

1. Open `WB260414-00001`
2. Switch to `Trace & Evidence`
3. Confirm `Trace Timeline` and `Evidence Viewer` render as full-width sections
4. Confirm fallback trace/evidence lists still appear below for troubleshooting

## Risk

- The `js_class="logistics_waybill_form"` mount path is now the primary enhanced rendering path again.
- If the widgets still fail to appear, the next check should be whether the custom form renderer is being applied to the inherited waybill form view at runtime.
