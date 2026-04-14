# 2026-04-13 logistics_web 正式 addon 设计稿

## 背景

当前项目已明确：

- 不建议另起完全独立的前端工程
- 前端负责人需要有相对独立、边界清楚的代码归属区
- 前端增强能力应在 Odoo addon 体系内集中承接

因此，需要为 `custom_addons/logistics_web` 输出正式设计稿。

## 本次新增

- `ai-code/docs/architecture/logistics_web_addon_design.md`

## 核心结论

- `logistics_web` 定位为前端增强层与统一 UI 承载层
- 业务基础视图留在 `logistics_dispatch / logistics_trace_core / logistics_trace_exception`
- 工作台、老板页、时间线 widget、证据 viewer、通用组件集中到 `logistics_web`
- 接口策略继续遵循“RPC 为主，少量 controller 为补充”
