# 2026-04-14 evidence real preview and mock cleanup

## Objective

Make the current `Trace & Evidence` frontend stop pretending evidence images exist when they do not, and render real previews whenever the backend already provides usable image addresses.

## Scope

Updated:

- `custom_addons/logistics_web/views/logistics_web_waybill_views.xml`
- `custom_addons/logistics_web/static/src/js/widgets/evidence_viewer_widget.js`
- `custom_addons/logistics_web/static/src/js/widgets/trace_timeline_widget.js`
- `custom_addons/logistics_web/static/src/js/views/logistics_waybill_form_view.js`
- `custom_addons/logistics_web/static/src/js/widgets/trace_evidence_field_widgets.js`
- `custom_addons/logistics_web/static/src/xml/widget_templates.xml`
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

## Main Changes

### Evidence viewer now prefers real image rendering

- The waybill evidence widget now renders a real stage image when `preview_url`, `full_url`, or a directly usable `image_access_key` is available.
- Thumbnail items use the same real-image path instead of always showing mock preview blocks.
- If an image fails to load, the widget falls back to a descriptive placeholder for that evidence item instead of showing a broken image frame forever.

### Full-image opening is more tolerant

- `Open Full Image` now falls back in this order:
  - `full_url`
  - `preview_url`
  - directly usable `image_access_key`
- Wrapped string values such as `"D:\path\image.jpg"` are normalized before opening.
- Windows local paths are converted to `file:///...` form on the frontend so local test data can degrade more gracefully during integration.

### Built-in fake evidence samples were removed

- `EvidenceViewerWidget` no longer ships with hard-coded sample evidence cards.
- The non-primary field-widget version of the evidence viewer follows the same rule.
- The evidence query path in the enhanced waybill form no longer fabricates placeholder evidence items when the backend read fails.

### Trace widget mock defaults were also tightened

- `TraceTimelineWidget` no longer contains built-in sample timeline cards.
- Real trace records or the renderer-level degraded summary are now the only sources shown in the waybill detail area.

### Waybill fallback hint now passes Odoo view validation

- Replaced the invalid bare `<label>` helper text in the waybill enhanced page with an `o_form_label` block.
- This lets `logistics_web` upgrade cleanly during module validation instead of failing before assets can refresh.

## Expected Result

After upgrading `logistics_web` and refreshing backend assets:

- real image URLs should display directly inside `Trace & Evidence`
- `Open Full Image` should open a usable image address when one exists
- missing or broken evidence images should show an honest placeholder state
- widget-level fake evidence and trace samples should no longer appear during failures

## Risk

- `file:///` conversion only helps local test data that is already reachable on the same machine; it is not a replacement for the proper backend image service integration.
- If the backend provides unusable addresses, the widget will now show a truthful degraded state instead of masking the issue with mock content.
