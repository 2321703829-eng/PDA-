# 2026-04-27 AGENTS baseline synced with phase4 customer_line and image reading chain

## 本次变更

更新文档：

- `d:/Desktop/Odoo/AGENTS.md`
- `d:/Desktop/Odoo/ai-code/AGENTS.md`

## 变更目的

- 修正 `AGENTS.md` 中已经过期的执行主线表述。
- 把当前四期前端已经稳定的 `customer_line` 主阅读链和图片阅读链同步进入口基线。
- 避免团队继续把旧的 `waybill -> waybill order lines` 当成当前有效主链。

## 变更摘要

- 将执行主线从：
  - `wave -> batch -> waybill -> waybill order lines`
  调整为：
  - `wave -> batch -> waybill -> customer_line -> order_line -> goods_line`
- 新增：
  - 页面主阅读链：`waybill -> customer_line -> order_line`
  - 图片阅读链：`waybill -> customer_line -> 图片预览 / 留痕 / 证据`
- 保留：
  - `waybill` 是当前 trace 主对象
- 补充说明：
  - `customer_line` 是当前门店侧主阅读入口
  - `customer_line` 不替代 `trace_event` 的正式对象锚点
- 同步修正模块方向说明：
  - `logistics_trace_evidence` 不再标记为 future

## 当前边界

- 本次只修改入口基线文档，不改业务代码。
- 本次不改 trace/evidence/exception 的详细专题设计。

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不影响
- 本次无代码与数据结构改动

## 验证方法

- 检查两份 `AGENTS.md` 是否都已使用 `customer_line` 新主链
- 检查两份 `AGENTS.md` 是否都明确区分：
  - `customer_line` 页面阅读入口
  - `trace_event` 正式对象锚点

## 风险点

- `docs/context/` 与部分历史说明文档中仍可能存在旧的 `waybill order lines` 表述，后续需要继续分批回扫。
