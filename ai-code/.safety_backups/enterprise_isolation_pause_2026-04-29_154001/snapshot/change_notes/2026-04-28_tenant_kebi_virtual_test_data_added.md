# 2026-04-28 tenant_kebi Virtual Test Data Added

## Background

After `tenant_kebi` became the first local `P0` validation tenant, manual testing still lacked a clean and recognizable demo dataset.

## What changed

Added a tenant-local virtual dataset inside `tenant_kebi` only:

- three obvious demo store records
- three `KEBI`-prefixed waybills
- basic customer line / order line / goods line coverage
- trace and evidence coverage
- one open exception scenario

## Practical result

The tenant now includes a small but usable manual-testing dataset for:

- basic waybill reading
- trace and evidence reading
- exception reading and state flow
- permission and role regression

## Synced docs

- `专题设计/企业隔离设计/02_验收与联调/2026-04-28_tenant_kebi虚拟测试数据说明.md`
- `专题设计/企业隔离设计/02_验收与联调/README.md`
