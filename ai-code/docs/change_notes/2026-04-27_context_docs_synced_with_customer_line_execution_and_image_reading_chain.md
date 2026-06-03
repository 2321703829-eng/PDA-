# 2026-04-27 docs/context synced with customer_line execution and image reading chain

## 本次变更

更新文档：

- `docs/context/README.md`
- `docs/context/odoo_logistics_context.md`
- `docs/context/odoo_logistics_execution_trace_context.md`
- `docs/context/odoo_logistics_order_trace_exception_draft.md`
- `docs/context/odoo_logistics_feasibility.md`
- `docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`

## 变更目的

- 对 `docs/context/` 做一轮和当前主链直接相关的口径回扫。
- 清理仍在入口层出现的旧表述，例如：
  - `waybill -> waybill order lines`
  - `运单下订单列表`
  - 只写 `波次 / 批次 / 运单` 而漏掉 `customer_line / order_line / goods_line`
- 把当前已经稳定的页面主阅读链和图片阅读链同步到上下文层。

## 变更摘要

- 统一补成：
  - 执行与数据主链：`wave -> batch -> waybill -> customer_line -> order_line -> goods_line`
  - 页面主阅读链：`waybill -> customer_line -> order_line`
  - 图片阅读链：`waybill -> customer_line -> 图片预览 / 留痕 / 证据`
- 继续保留：
  - `waybill` 是当前 trace 主对象
  - 正式证据对象仍围绕 `trace_event`
- 明确新增：
  - `customer_line` 是当前门店侧主阅读入口
  - `customer_line` 不替代 `trace_event` 的正式对象锚点

## 当前边界

- 本次只改上下文文档，不改业务代码。
- 本次只回扫和主链直接相关的内容，不做全量历史文档清洗。

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不影响
- 本次无代码与数据结构改动

## 验证方法

- 检查 `docs/context/` 入口文档是否已经统一使用 `customer_line` 新主链
- 检查上下文文档是否都明确区分：
  - `customer_line` 页面主阅读入口
  - `trace_event` / `evidence` 正式对象链

## 风险点

- `docs/context/` 之外的历史桥接稿、归档稿和其他目录仍可能保留旧口径，后续需要继续分批回扫。
