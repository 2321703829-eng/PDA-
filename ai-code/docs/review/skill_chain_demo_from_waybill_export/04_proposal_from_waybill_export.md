# 示例 04：后端技术方案

## Objective

- 为 `from_waybill` 提供一条正式导出技术链，支持任务创建、结果回读、文件下载和错误报告下载。

## Odoo Benchmark

### Odoo 原生已有能力

- 列表导出可以做临时字段导出
- 视图、动作、权限、HTTP 路由和附件基础设施可复用

### Odoo 原生不足

- 不提供正式的多层导出任务链
- 不提供 `task_no -> result -> lines -> errors -> download` 这种结果回读链
- 不适合直接承载当前四 Sheet 正式模板导出需求

### 方案选择

- 不直接复用原生列表导出作为正式方案
- 复用当前项目导入链的方法论
- 在自定义模块中建立独立导出任务模型和服务层

## Outcome / Behavior / Boundary

### Outcome

- 运单导出成为正式业务能力，而不是临时工具能力

### Behavior

- 运单列表页和详情页都可发起导出
- 服务层同步执行首轮导出
- 结果页围绕 `task_no` 回读

### Boundary

- 仅 `from_waybill`
- 仅标准四 Sheet `xlsx`
- 不进入异步队列重构

## Design Decision

### 1. 模型与任务链

采用独立导出任务模型：

- `logistics.export.source.scope`
- `logistics.export.task`
- `logistics.export.task.line`
- `logistics.export.error.line`

理由：

- 导出与导入行为方向不同
- 导出需要结果文件、过期时间和下载链
- 不能把所有导出逻辑塞进既有 `import_task`

### 2. 服务层

服务层集中在 `logistics_web/services/dispatch_main_export_service.py`，负责：

- 建任务
- 取数
- 组装工作簿
- 落盘
- 回写结果
- 返回结果 DTO

### 3. 控制器层

控制器集中在 `logistics_web/controllers/logistics_web_export.py`，负责：

- 参数接收
- 服务调用
- 异常转译
- JSON 响应与文件响应

### 4. 前端入口与结果页

- 列表页导出按钮走 `POST /api/admin/logistics/exports/waybill`
- 详情页按钮通过对象方法发起导出并打开结果页
- 导出结果页复用导入结果页的阅读节奏，但保留独立客户端动作

## Contract Surface

### 主对象与主链位置

- 主对象：`logistics.dispatch.waybill`
- 位置：执行主线中的运单层，不进入追溯链

### 关键模型 / 字段 / 状态

- 任务模型：`export_task*`
- 关键字段：`task_no`、`entry_type`、`package_structure`、`status`
- 任务状态与行状态需与正式设计稿一致

### API / Route / Action

- `POST /api/admin/logistics/exports/waybill`
- `GET /api/admin/logistics/exports/tasks/{task_no}/...`
- 导出结果客户端动作

### 导入导出或任务链契约

- `entry_type = from_waybill`
- `package_structure = dispatch_main_four_sheet`
- 结果回读固定使用 `task_no`

### 权限与升级影响

- 需要补导出任务相关 ACL
- 升级后必须验证入口按钮与正式任务模型权限口径一致

## Affected Modules / Files

- [dispatch_main_export_service.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/dispatch_main_export_service.py:1)
- [logistics_web_export.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/logistics_web_export.py:1)
- [logistics_web_waybill_views.xml](/d:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_waybill_views.xml:1)
- [logistics_dispatch security ACL](</d:/Desktop/Odoo/custom_addons/logistics_dispatch/security/ir.model.access.csv:1>)

## Verify

- 模块升级可跑
- 列表页与详情页入口可触发
- `task_no -> result -> lines -> errors -> download` 可回读
- 导出 ACL 与页面入口口径一致

## Risks / Open Questions

- 首轮同步执行在大批量场景下可能成为瓶颈
- 后续客户画像、货物画像导出接入后，结果页分支要继续收口而不能破坏已上线 `from_waybill`
