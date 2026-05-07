# 2026-04-13 logistics_exception 回调为 logistics_trace_exception 设计

## 本次变更

- 新增 `docs/architecture/logistics_trace_exception_addon_design.md`
- 将 `docs/architecture/logistics_exception_addon_design.md` 回调为历史入口说明

## 主要调整

- 不再继续深化 `logistics_exception` 作为旧阶段异常模块
- 正式把异常层模块收口到 `logistics_trace_exception`
- 明确异常对象建立在 `dispatch + trace_core` 上下文之上
- 明确异常层与证据层、工作台、老板页之间的关系

## 说明

- 本次仅修改文档
- 未进行代码实现、编译、模块升级或服务启动

