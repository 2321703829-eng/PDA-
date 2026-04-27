# 2026-04-27 high concurrency query investigation checklist v1 added

## What changed

- added a first-round investigation checklist for high-concurrency query capacity
- scoped the checklist to current logistics backend query hotspots instead of generic performance advice
- organized the investigation path by page, API, SQL observation, pressure test steps, and pass/fail signals

## Files

- [高并发查询调查清单_v1.md](/d:/Desktop/Odoo/ai-code/docs/dev/高并发查询调查清单_v1.md)

## Key points

- treat homepage, dashboard, stats center, and task result pages as the main query investigation targets
- separate “can investigate” from “can already prove concurrency capacity”
- require SQL-level observation before drawing conclusions
- highlight current risks around repeated `search_count` and Python-side full-record aggregation
