# 2026-04-18 前端 GitHub 同步分支 / 模块 / 模型结构说明

本说明对应已推送到 GitHub 的前端优化同步提交：

- 分支：`feat-image-4a`
- 提交：`ed5a5c950c80 feat(logistics_web): sync frontend optimization progress`

## 1. 代码在哪个分支

- 当前前端优化进度已推送到 GitHub 分支：`feat-image-4a`

## 2. 改了哪几个模块

本次代码层实际涉及的 Odoo 自定义模块主要是：

1. `logistics_web`
2. `logistics_dispatch`

补充说明：

- 同步中还包含了 `ai-code/前端设计/`、`ai-code/docs/change_notes/`、`ai-code/scripts/`、前端检查 skill 文档等设计与检查资料。
- 但如果只按 Odoo 业务模块口径统计，本次主要改动模块就是 `logistics_web` 和 `logistics_dispatch`。

## 3. 有没有新增数据库字段或者改了模型结构

结论：`有`。

### 3.1 明确新增的数据库字段

本次确认新增了 1 个真实模型字段：

1. `hr.employee.logistics_has_own_vehicle`
   - 所在模块：`logistics_web`
   - 落点文件：`custom_addons/logistics_web/models/logistics_driver_service.py`
   - 字段类型：`fields.Boolean`
   - 作用：司机管理中标记“是否有自有车”

### 3.2 明确发生的模型结构调整

本次还存在已有模型字段的删减/调整：

1. `logistics.dispatch.batch`
   - 移除了字段：`stock_picking_batch_id`
   - 落点文件：`custom_addons/logistics_dispatch/models/logistics_dispatch_batch.py`

2. `logistics.dispatch.waybill`
   - 移除了字段：`stop_ids`
   - 移除了字段：`stop_count`
   - 落点文件：`custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py`

### 3.3 不计入数据库结构变更的内容

下面这些属于模型方法、服务能力、控制器、页面资产、权限配置或文案/视图变更，不算新增数据库字段：

- `logistics_web/models/logistics_dashboard_service.py`
- `logistics_web/models/logistics_driver_service.py` 中除 `logistics_has_own_vehicle` 外的大部分 driver service 方法
- `logistics_web/models/logistics_stats_service.py`
- `logistics_web/controllers/*`
- `logistics_web/static/src/js/*`
- `logistics_web/static/src/xml/*`
- `logistics_web/static/src/scss/*`
- `logistics_web/security/logistics_web_security.xml`

## 4. 一句话版

- 分支：`feat-image-4a`
- 模块：`logistics_web`、`logistics_dispatch`
- 模型结构：`有变化`
  - 新增字段：`hr.employee.logistics_has_own_vehicle`
  - 删除/调整字段：`logistics.dispatch.batch.stock_picking_batch_id`、`logistics.dispatch.waybill.stop_ids`、`logistics.dispatch.waybill.stop_count`
