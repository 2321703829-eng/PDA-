# 示例 02：结构化需求

## Objective

- 建立 `from_waybill` 首轮正式导出链路，形成与当前导入链一致的任务式结果回读体验。

## Background

- 当前项目已经形成正式导入链：`task_no -> result -> lines -> errors -> error-report`。
- 运单导出需要一条对用户可见、对后续扩展可复用的正式链路，而不是停留在原生列表临时导出。

## Scope / Out of Scope

范围内：

- 入口：运单列表页、运单详情页
- 正式导出任务：`export_source_scope -> export_task -> export_task_line -> export_error_line`
- 文件结构：四 Sheet `xlsx`
- 结果页：摘要、行结果、错误明细、错误报告、主文件下载

范围外：

- `from_batch / from_customer`
- 图片证据导出
- 导出中心历史页面
- 复杂离线分片和超大任务调度

## Actors / Main Object

- 角色：后台物流用户
- 主对象：`logistics.dispatch.waybill`
- 相关对象：`customer_line`、`order_line`、`goods_line`

## Outcome / Behavior / Boundary

### Outcome

- 用户可以稳定发起 `from_waybill` 导出。
- 系统可以生成标准四 Sheet 文件并回写任务结果。
- 结果页可以围绕 `task_no` 完成结果回读和下载。

### Behavior

- `POST /api/admin/logistics/exports/waybill` 接收导出请求。
- 系统校验选中运单的可读权限。
- 系统创建任务、任务行、结果文件及错误明细。
- 结果页继续使用 `task_no` 为主键读取任务结果。
- 列表页与详情页发起成功后都跳转到导出结果页。

### Boundary

- 首轮只做 `from_waybill`
- 首轮只做 `dispatch_main + standard_xlsx + dispatch_main_four_sheet`
- 首轮只验证同步执行链，不做异步架构升级

## Main Flow / Exception Flow

### Main Flow

1. 用户发起导出。
2. 系统创建导出任务。
3. 系统展开 waybill 下游数据。
4. 系统生成工作簿并落盘。
5. 系统回写结果，前端按 `task_no` 打开结果页。

### Exception Flow

1. 无权限时，接口返回错误响应，任务不创建。
2. 运单存在但下游数据缺失时，任务行可进入 `skipped` 或 `failed`。
3. 文件已过期时，下载接口返回过期错误。

## Rules / Data / States

### 关键规则

- `from_waybill` 是入口类型，不等于文件内部包结构。
- 文件内部固定四 Sheet：
  - `Waybill`
  - `CustomerLine`
  - `OrderLine`
  - `GoodsLine`
- 结果回读固定围绕 `task_no`

### 任务状态

- `pending`
- `running`
- `success`
- `partial_failed`
- `failed`
- `expired`
- `cancelled`

### 行状态

- `pending`
- `success`
- `failed`
- `skipped`

## Interfaces / Page Impact

### 接口

- `POST /api/admin/logistics/exports/waybill`
- `GET /api/admin/logistics/exports/tasks/{task_no}`
- `GET /api/admin/logistics/exports/tasks/{task_no}/lines`
- `GET /api/admin/logistics/exports/tasks/{task_no}/errors`
- `GET /api/admin/logistics/exports/tasks/{task_no}/error-report`
- `GET /api/admin/logistics/exports/tasks/{task_no}/download`

### 页面

- 运单列表页新增导出入口
- 运单详情页新增导出结果按钮
- 新增导出结果页客户端动作

## Acceptance / Open Questions

### Acceptance

- 列表页与详情页都能发起 `from_waybill` 导出
- 成功后能打开结果页
- 结果页能回读摘要、行结果、错误明细
- 文件和错误报告可下载
- 访问权限与页面入口口径一致

### Open Questions

- 后续多对象导出是否完全共享结果页
- 同步执行上限在哪里，需要什么条件切到异步
