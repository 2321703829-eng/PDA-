# 2026-04-28 enterprise_isolation_plan_a_to_b_impact_and_migration_note_added

## What changed

- Added a dedicated design note for migrating from:
  - plan A: subdomain -> `dbfilter` -> database
  - to plan B: single domain + path prefix -> gateway mapping -> `X-Odoo-Database`
- Summarized:
  - what changes
  - what mostly does not change
  - the main risks
  - a recommended migration sequence

## Files

- `专题设计/企业隔离设计/00_导航与总纲/2026-04-28_方案A调整到方案B的影响清单与迁移步骤.md`
- `专题设计/企业隔离设计/README.md`

## Result

- The enterprise-isolation topic now distinguishes more clearly between:
  - current route-selection comparison and recommendation
  - the actual A -> B migration impact and step-by-step transition view
