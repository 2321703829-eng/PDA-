# 2026-04-28 enterprise_isolation_p0_route_selection_comparison_and_recommendation_added

## What changed

- Added a new P0 design note for enterprise-isolation route selection comparison and recommendation.
- Kept the original `dbfilter` naming / domain / database mapping spec unchanged.
- Added a new comparison note covering:
  - subdomain-to-database routing
  - single-domain path-prefix routing
  - why unified-login then session-based dynamic database switching is not recommended for current `P0 / P1`
- Synced the new note into:
  - enterprise-isolation topic README
  - `P0 / P1` master design doc
  - `P0 / P1` detailed master work plan

## Files

- `专题设计/企业隔离设计/00_导航与总纲/2026-04-28_企业隔离P0路由选库方案对比与推荐说明.md`
- `专题设计/企业隔离设计/README.md`
- `专题设计/企业隔离设计/00_导航与总纲/2026-04-28_企业隔离P0P1总设计文档.md`
- `专题设计/企业隔离设计/00_导航与总纲/2026-04-28_企业隔离P0P1详细总工作计划.md`

## Result

- The original subdomain + `dbfilter` spec remains the current standard baseline.
- The topic now explicitly recognizes path-prefix + gateway database selection as a viable alternative if operations do not want many subdomains.
- The topic also explicitly marks unified-login then session-based database switching as a future platformization direction rather than a current `P0 / P1` delivery path.
