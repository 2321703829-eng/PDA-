# 2026-04-28 enterprise_isolation_route_selection_note_adds_subdomain_ops_pressure_guidance

## What changed

- Updated the P0 route-selection comparison note with an explicit operations-pressure judgment for plan A subdomain scale.
- Added a practical range-based view for when subdomain count usually starts to create sustained ops pressure.

## Files

- `专题设计/企业隔离设计/00_导航与总纲/2026-04-28_企业隔离P0路由选库方案对比与推荐说明.md`

## Result

- The route-selection note now explains not only the technical comparison between plan A / B / C, but also when plan A is likely to become operationally heavy.
- The note now gives a clearer handoff point for when the team should seriously evaluate moving from subdomain routing to path-prefix routing.
