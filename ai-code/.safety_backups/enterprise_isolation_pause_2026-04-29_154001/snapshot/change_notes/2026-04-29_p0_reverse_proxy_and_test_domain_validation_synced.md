# 2026-04-29 P0 Reverse Proxy And Test Domain Validation Synced

## Background

The local `P0` validation had already completed direct tenant/database routing, but still needed one more round of host-based reverse-proxy and test-domain verification.

## What changed

Confirmed and synced the following local validation results:

- `kebi.tianshu.test -> 127.0.0.1:8090 -> tenant_kebi`
- `dev.tianshu.test -> 127.0.0.1:8090 -> odoo_logistics_dev`
- `kebi.tianshu.test:8090/web/login` is available
- `dev.tianshu.test:8090/web/login` is available
- `kebi.tianshu.test:8090/web/database/selector` returns to `/web/login`

## Synced docs

- `专题设计/企业隔离设计/02_验收与联调/2026-04-28_企业隔离P0真实环境参数登记单.md`
- `专题设计/企业隔离设计/02_验收与联调/2026-04-28_企业隔离P0_kebi租户执行清单.md`
- `专题设计/企业隔离设计/05_提交包/2026-04-28_企业隔离P0P1本轮最终交付说明.md`
