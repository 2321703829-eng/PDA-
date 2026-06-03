# 2026-04-28 Enterprise Isolation Rebaseline Image Package As Optional Enhancement

## Background

After the latest implementation and manual verification round:

- `trace / evidence / exception / waybill` main chain is already running
- `image_package` already supports import, matching, linking, failure recording, retry, and import-center access

Business feedback also confirmed that image-package enhancement is not a high-priority demand in the current phase.

## Decision

Rebaseline the current topic as follows:

- `image_package` is no longer treated as a main `P1` gap
- `image_package` is treated as:
  - already sufficient for current `P1`
  - optional enhancement for later rounds

## New current priorities

The next-step focus is now:

1. `P0` real-environment implementation
2. real-account permission regression
3. delivery closeout

## Synced docs

- `专题设计/企业隔离设计/05_提交包/2026-04-28_企业隔离P1本轮剩余待办项.md`
- `专题设计/企业隔离设计/00_导航与总纲/2026-04-28_企业隔离P0P1总设计文档.md`
- `专题设计/企业隔离设计/00_导航与总纲/2026-04-28_企业隔离P0P1详细总工作计划.md`

