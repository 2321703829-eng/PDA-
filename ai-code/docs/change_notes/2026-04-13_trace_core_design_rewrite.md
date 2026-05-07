# 2026-04-13 logistics_trace 回调为 logistics_trace_core 设计

## 本次变更

- 新增 `docs/architecture/logistics_trace_core_addon_design.md`
- 将 `docs/architecture/logistics_trace_addon_design.md` 回调为历史入口说明

## 主要调整

- 不再继续深化 `logistics_trace` 作为单一粗粒度模块
- 正式把留痕核心层模块收口到 `logistics_trace_core`
- 明确批次级与运单级留痕事件模型思路
- 明确 `logistics_trace_core` 与 `logistics_dispatch / logistics_trace_evidence / logistics_trace_exception` 的边界

## 说明

- 本次仅修改文档
- 未进行代码实现、编译、模块升级或服务启动

