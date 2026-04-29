# 2026-04-29 `P0` ops handoff instruction note added

## What changed

- added `专题设计/企业隔离设计/02_验收与联调/2026-04-29_P0发给运维的正式部署执行指令稿.md`
- updated `专题设计/企业隔离设计/02_验收与联调/README.md`
- updated `专题设计/企业隔离设计/02_验收与联调/2026-04-29_P0正式部署与正式验收剩余工作清单.md`

## Why

- the remaining `P0` work now depends on formal environment execution rather than local repository-only work
- a direct ops handoff note is needed so DNS, reverse proxy, and formal `dbfilter` rollout can be executed without re-explaining the design context

## Result

- the current `P0` package now includes:
  - a formal proxy note
  - an acceptance header template
  - a concise ops handoff instruction note
- the next stage can proceed through formal environment rollout and acceptance backfill
