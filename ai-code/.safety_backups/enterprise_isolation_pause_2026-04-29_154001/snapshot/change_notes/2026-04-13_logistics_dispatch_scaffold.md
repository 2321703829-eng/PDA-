# 2026-04-13 logistics_dispatch 模块骨架与运单列表首版落地

## 本次新增

- `custom_addons/logistics_dispatch/`
- 基础模型：
  - `logistics.dispatch.wave`
  - `logistics.dispatch.batch`
  - `logistics.dispatch.waybill`
  - `logistics.dispatch.waybill.order.line`
- 基础序列、ACL、菜单、列表/表单/搜索视图

## 本次目标

按 `前端开发任务拆分清单.md` 中的 `FE-P0-001` 起步，给运单追溯列表页提供真实模块落点，而不是继续停留在设计文档层。

## 本次完成的重点

1. 新建 `logistics_dispatch` 真实 addon 骨架
2. 落下 `Wave / Batch / Waybill / Waybill Order Line` 最小模型
3. 提供 `Waybill Tracking` 列表、搜索、详情页
4. 提供 `Waves / Batches / Waybill Tracking` 菜单入口
5. 统一按 Odoo 19 的 `list` 视图口径收口 XML

## 当前仍未做

- 未执行模块安装或升级
- 未落 Smart Button
- 未接入 `logistics_trace_core`
- 未接入 `logistics_trace_exception`
- 留痕/证据/异常数量当前仍是占位字段

## 下一步建议

1. 继续 `FE-P0-002`：运单详情页基础表单增强
2. 或继续 `FE-P0-003`：当前异常列表页真实模块落点
3. 然后再补 `trace_core` 和 `trace_exception` 的真实骨架

