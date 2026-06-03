# 2026-04-13 logistics_dispatch 运单详情页首轮增强

## 本次修改

- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`

## 本次目标

继续按 `前端开发任务拆分清单.md` 推进 `FE-P0-002`，让 `Waybill` 不只是一个能打开的表单，而是开始具备“详情页”结构。

## 本次完成的重点

1. 增加 `order_line_count` 聚合字段
2. 增加运单详情页 `button box`
3. 增加跳转批次、跳转波次、查看运单明细的方法
4. 补强标题区与摘要区结构
5. 让执行上下文、聚合信息、订单明细入口更接近设计稿

## 当前仍未做

- 未接入 trace/evidence/exception 的真实 smart button
- 未接入时间线 widget
- 未接入证据区 widget
- 未执行模块安装与升级验证

## 下一步建议

1. 继续 `FE-P0-003`：异常列表页真实模块落点
2. 或继续 `FE-P0-006/007` 之前先把 `trace_core` 骨架建起来

