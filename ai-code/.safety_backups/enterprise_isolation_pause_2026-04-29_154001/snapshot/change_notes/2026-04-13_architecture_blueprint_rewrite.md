# 2026-04-13 架构入口与 custom_addons 蓝图重写

## 本次变更

- 重写 `docs/architecture/ARCHITECTURE.md`
- 重写 `docs/architecture/custom_addons_blueprint.md`

## 主要调整

- 从旧的 `logistics_order / shipment_order` 主线切换到 `wave / batch / waybill` 主线
- 明确区分“当前仓库实际目录现状”和“目标模块蓝图”
- 引入 `logistics_dispatch / logistics_trace_core / logistics_trace_evidence / logistics_trace_exception / logistics_trace_dashboard / logistics_trace_rule` 这套目标模块理解
- 让架构文档和前端总体设计、运单主对象文档对齐

## 说明

- 本次仅修改文档
- 未进行代码实现、编译、模块升级或服务启动

