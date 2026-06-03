# 2026-04-28 enterprise_isolation_route_selection_note_drops_plan_c

## What changed

- Trimmed the P0 route-selection comparison note to only keep:
  - plan A: subdomain -> `dbfilter` -> database
  - plan B: single domain + path prefix -> gateway mapping -> `X-Odoo-Database`
- Removed the previous plan C discussion from that note because it is no longer under consideration in the current topic scope.

## Files

- `专题设计/企业隔离设计/00_导航与总纲/2026-04-28_企业隔离P0路由选库方案对比与推荐说明.md`

## Result

- The note now has a cleaner scope and matches the current decision space more closely.
- Future readers will no longer misread it as a three-option comparison for the current phase.
