# 示例 01：需求摘要

## Objective

- 为运单视角提供一条标准批量导出链路。
- 让用户可以从运单列表页或运单详情页发起导出，并进入结果页查看任务摘要、行结果、错误明细和下载入口。

## Current Problem

- 当前 Odoo 原生导出更适合临时列表字段导出，不适合当前物流主线下的多层结构导出。
- 现有导入链已经围绕 `task_no`、结果页、错误明细和四 Sheet 模板收口，但导出侧还缺少同风格的正式闭环。
- 如果没有正式导出链，用户只能拿到临时导出结果，无法稳定复用到后续修订和再导入流程。

## Main Object / Main Line

- 主对象：`waybill`
- 主线位置：`wave -> batch -> waybill -> waybill order lines`
- 本次导出仍围绕 `waybill` 展开，不扩到 `trace / evidence / exception`

## Scope / Out of Scope

范围内：

- `from_waybill` 入口
- `task_no -> result -> lines -> errors -> download` 结果链
- 标准四 Sheet `xlsx`
- 列表页与详情页入口

范围外：

- `from_batch`
- `from_customer`
- 图片 ZIP 导出
- 导出中心历史页
- 异步任务队列重构

## Main Flow Sketch

1. 用户在运单列表页勾选运单，或在运单详情页发起导出。
2. 系统创建正式导出任务并生成 `task_no`。
3. 系统读取运单及其下游 `customer_line / order_line / goods_line`。
4. 系统生成四 Sheet `xlsx`，落盘并回写任务结果。
5. 前端结果页按 `task_no` 回读摘要、行结果、错误明细与下载链接。

## Key Constraints

- 入口类型是 `from_waybill`，但文件内部正式层级仍是 `Waybill / CustomerLine / OrderLine / GoodsLine`。
- 导出任务结构要复用导入任务链的阅读节奏，但不直接复用 `import_task` 模型。
- 首轮允许同步执行，只要结果链闭环稳定。

## Open Questions

- 后续 `from_batch / from_customer` 是否完全复用同一任务读取链
- 导出量变大后是否需要改为异步 worker
- 运单导出与后续客户画像、货物画像导出的结果页分支是否继续共用一套客户端动作

## Suggested Next Step

- 继续展开为结构化需求，锁定入口类型、包结构、任务链、状态与结果页契约。
