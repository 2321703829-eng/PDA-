# 2026-04-29 `P0` formal subdomain, proxy note, and acceptance headers prepared

## What changed

- fixed the current formal test subdomain for `kebi` as `kebi.tianshu.cn`
- added `专题设计/企业隔离设计/02_验收与联调/2026-04-29_P0方案A正式反向代理配置说明.md`
- added `专题设计/企业隔离设计/02_验收与联调/2026-04-29_P0正式验收表头与回填模板.md`
- updated `专题设计/企业隔离设计/02_验收与联调/2026-04-28_企业隔离P0真实环境参数登记单.md`
- updated `专题设计/企业隔离设计/02_验收与联调/2026-04-29_P0正式部署与正式验收剩余工作清单.md`
- updated `专题设计/企业隔离设计/02_验收与联调/2026-04-29_P0正式部署执行顺序与边界说明.md`
- updated `专题设计/企业隔离设计/02_验收与联调/README.md`

## Why

- move `P0` from generic remaining-work discussion into concrete formal-environment preparation
- lock the current formal test-domain assumption before DNS and proxy rollout
- prepare an operator-facing reverse-proxy note and an acceptance backfill template in advance

## Result

- current `P0` phase now has a fixed formal test subdomain assumption:
  - `kebi.tianshu.cn`
- the team now has:
  - a formal proxy configuration note
  - a formal acceptance header / backfill template
  - a resynced parameter register and remaining-work checklist
