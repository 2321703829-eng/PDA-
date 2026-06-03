# 2026-04-23 导入中心与结果页 task_no 路由收口

## 本次变更

- 调整前端导入中心与结果页的跳转参数，优先使用 `task_no`，同时兼容旧 `import_batch_no`。
- 新增后端任务结果读取与错误报告下载路由：
  - `/api/admin/logistics/imports/tasks/<task_no>`
  - `/api/admin/logistics/imports/tasks/<task_no>/error-report`
- 保留旧路由：
  - `/api/admin/logistics/imports/waybill-standard/result`
  - `/api/admin/logistics/imports/waybill-standard/error-report`
  作为兼容入口，统一转到新的任务读取逻辑。
- 更新 `WaybillStandardImportService` 返回结构，补充：
  - `task_no`
  - `object_type`
  - `object_type_label`
  - `total_count / success_count / fail_count`
  - `summary_message`
  - `source_file`
  - `error_report`
  - `next_actions`

## 变更原因

- 四期导入接口文档已经以 `task_no` 和 `/imports/tasks/...` 为正式结果回读口径。
- 现有前端和 controller 仍停留在 `import_batch_no` 与 `/waybill-standard/result` 命名，容易让联调继续沿用旧链路。
- 本次先完成“参数名 / 路由名 / 返回字段名”的兼容型收口，不打断现有批次模型链路。

## 当前实现策略

- 当前结果读取底层仍然由 `logistics.import.batch` 提供数据来源。
- `task_no` 先与现有 `batch.name` 保持一致，用于完成前端跳转和后端任务路由收口。
- 新旧字段暂时并行返回：
  - 新字段给四期结果页与新接口使用
  - 旧字段保留给历史页面和兼容逻辑使用

## 涉及文件

- `custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- `custom_addons/logistics_web/static/src/js/actions/import_result_action.js`
- `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`
- `custom_addons/logistics_web/static/src/xml/import_result_templates.xml`
- `custom_addons/logistics_web/controllers/logistics_web_import_v3.py`
- `custom_addons/logistics_web/services/waybill_standard_import_service_v2.py`

## 备注

- 本次没有把底层结果来源完全切换到 `logistics.import.task`，属于兼容迁移的第一步。
- 后续如果继续推进，应把预校验、确认导入、行结果、错误明细也逐步迁到正式导入任务模型。
