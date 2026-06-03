# 2026-04-20 boss trace visual round 2

## Goal

- remove the gray, low-energy feeling from the management board hero
- make first-screen summary cards feel like management decision cards instead of ordinary summary tiles

## Completed

- strengthened the management board hero selector so page-level hero styles reliably override the generic panel look
- refreshed the hero into a deeper blue-green decision palette with stronger contrast and stronger top-right / bottom-right lighting
- upgraded headline cards with:
  - stronger top accent strips
  - tone-aware background layers
  - larger value hierarchy
  - stronger hover elevation

## Files

- `custom_addons/logistics_web/static/src/scss/boss_trace.scss`

## Verify

- the management board hero should no longer read as a gray panel
- the first summary row should feel more like a decision layer than a normal dashboard card row
