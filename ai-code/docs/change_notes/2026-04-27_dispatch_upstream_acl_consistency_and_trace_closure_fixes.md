# 2026-04-27 Dispatch 上游 ACL、一致性与 Trace 闭环修复

## Objective

修复 `logistics_dispatch` 主链上游的 3 个高风险问题：

1. `wave / batch / waybill` 对普通内部用户开放过宽
2. `warehouse / batch / wave` 缺少后端一致性护栏
3. trace 完成状态不能回推执行态，`finished_waybill_count` 不闭环

## What Changed

### 1. 收紧 dispatch 主对象权限

- 新增 `group_logistics_dispatch_manager`
- `wave / batch / waybill` 对 `base.group_user` 改成只读
- `dispatch manager` 允许 `read/write/create`
- 两类角色都不允许 `unlink`
- 调度菜单、批次菜单、波次菜单改成仅 `dispatch manager` 可见

### 2. 补齐后端一致性护栏

- `batch` 在 `wave_id` 已知但 `warehouse_id` 未传时，会自动继承 `wave.warehouse_id`
- `batch` 新增后端约束：`batch.warehouse_id` 必须与 `wave.warehouse_id` 一致
- `waybill` 在 `batch_id` 已知但 `warehouse_id` 未传时，会自动继承 `batch.warehouse_id`
- `waybill` 新增后端约束：
  - 只要设置了 `batch_id`，就必须存在 `warehouse_id`
  - `waybill.warehouse_id` 必须与 `batch.warehouse_id` 一致
- `waybill` 的 `onchange(batch_id)` 改成始终同步仓库，而不是仅在空值时回填

### 3. 建立 trace 到执行态的最小闭环

- 在 `logistics_trace_core` 中新增 trace 驱动的执行态推进规则：
  - 有任意有效 trace：推进到 `in_transit`
  - 有 `arrive_store`：推进到 `arrived`
  - 有 `deliver_finish / signoff`：推进到 `done`
- 该规则采用“只前推、不回退、不覆盖 `cancelled`”策略
- `trace_event.create/write` 后会触发目标运单的执行态同步
- `batch.finished_waybill_count` 继续依赖 `waybill.state == "done"`，因此在 `signoff` trace 出现后会自动闭环

## Verify

### Parse

- AST OK:
  - `custom_addons/logistics_dispatch/models/logistics_dispatch_batch.py`
  - `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py`
  - `custom_addons/logistics_trace_core/models/logistics_dispatch_waybill.py`
  - `custom_addons/logistics_trace_core/models/logistics_trace_event.py`
- XML OK:
  - `custom_addons/logistics_dispatch/security/logistics_dispatch_security.xml`
  - `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- ACL CSV 结构读取正常

### Upgrade

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_trace_core,logistics_web --stop-after-init
```

升级成功。

### Shell Smoke

最小运行核验结果：

- `batch_auto_warehouse_from_wave = 1`
- `waybill_auto_warehouse_from_batch = 1`
- `owner_waybill_write_blocked = AccessError`
- `owner_batch_write_blocked = AccessError`
- `owner_wave_write_blocked = AccessError`
- `waybill_missing_warehouse_blocked = Waybill warehouse is required when batch_id is set.`
- `waybill_state_after_signoff_trace = done`
- `batch_finished_waybill_count_after_signoff_trace = 1`

## Notes

- 这轮没有把 `batch.state / wave.state` 也做成自动回推，只先收住 `waybill.state` 和 `finished_waybill_count` 的闭环
- 当前 trace 回推策略是“执行态推进”，不是“执行态回滚”
