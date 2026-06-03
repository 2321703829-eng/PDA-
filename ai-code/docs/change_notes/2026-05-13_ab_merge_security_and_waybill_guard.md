# 2026-05-13 A/B 合并后权限收口与运单强校验

## 本次调整

- 将 `wms_task_core`、`tms_dispatch_core`、`bi_ops_dashboard` 的模块依赖补齐到 `erp_base`
- 移除 B 线模块自建的本地 manager 角色承载，改为直接接入 A 线统一角色
- 将 WMS 任务访问控制收口到：
  - `erp_base.group_wms_operator`
  - `erp_base.group_wms_manager`
- 将 TMS 调度、司机任务、签收、异常、运费明细访问控制收口到：
  - `erp_base.group_tms_dispatcher`
  - `erp_base.group_tms_driver`
- 将 BI 快照访问控制收口到：
  - `erp_base.group_bi_viewer`
  - `erp_base.group_system_admin`
- 为 `group_tms_driver` 补了最小 record rule，限制司机只能访问与自己绑定司机画像相关的：
  - 派车单
  - 司机任务
  - 司机任务节点
  - 签收回单
  - 配送异常
- 在 `tms.dispatch.order` 生成司机任务时补了 `waybill` 必填校验
  - 若排线停靠点 `waybill_no` 找不到对应 `logistics.dispatch.waybill`，直接抛出校验错误
  - 避免继续生成缺失 `waybill_id` 的司机任务，防止后续签收、异常、BI 统计链条静默失真

## 影响范围

- `custom_addons/wms_task_core`
- `custom_addons/tms_dispatch_core`
- `custom_addons/bi_ops_dashboard`

## 目的

- 让 B 线模块真正接回 A 线统一权限模型
- 避免 `base.group_user` 兜底导致全员可见 WMS/TMS/BI 对象
- 避免司机看到非本人任务
- 避免 `TMS -> waybill` 关联断裂后仍继续生成任务数据
