# 2026-04-13 logistics_order 回调为 logistics_dispatch 设计

## 本次变更

- 新增 `docs/architecture/logistics_dispatch_addon_design.md`
- 将 `docs/architecture/logistics_order_addon_design.md` 回调为历史入口说明

## 主要调整

- 不再继续深化 `logistics_order / logistics.order` 作为执行主线模块
- 正式把执行主线模块收口到 `logistics_dispatch`
- 明确 `wave / batch / waybill / waybill_order_line` 这组推荐模型
- 明确 `logistics_dispatch` 与 `logistics_trace_core / evidence / exception` 的边界

## 说明

- 本次仅修改文档
- 未进行代码实现、编译、模块升级或服务启动

