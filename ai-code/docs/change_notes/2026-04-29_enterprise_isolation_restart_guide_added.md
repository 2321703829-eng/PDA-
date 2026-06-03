# 2026-04-29 enterprise isolation restart guide added

## What changed

- added `专题设计/企业隔离设计/05_提交包/2026-04-29_企业隔离计划后续重启操作说明.md`

## Why

- the enterprise isolation work was paused due to a newly inserted database-related requirement
- a clear restart guide is needed so the team can resume later from the preserved safety backup instead of re-deriving the recovery path

## Result

- the repo now contains a dedicated restart guide that explains:
  - where the preserved backup anchor is
  - which code, docs, and databases were retained
  - how to reopen work on a dedicated branch
  - how to restore local runtime and continue `P0 / P1`
