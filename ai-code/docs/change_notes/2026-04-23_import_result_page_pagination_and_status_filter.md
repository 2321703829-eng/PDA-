# 2026-04-23 导入结果页补齐分页与状态筛选

## 本次变更

- 结果页前端动作改为直接支持：
  - 行结果状态筛选
  - 行结果分页
  - 字段错误明细分页
- `GET /api/admin/logistics/imports/tasks/{task_no}/lines` 新增 `status` 查询参数，支持按 `pending / success / failed / skipped` 过滤。
- `lines` 与 `errors` 接口统一补充分页元信息：
  - `total_pages`
  - `has_prev`
  - `has_next`
  - `showing_from`
  - `showing_to`
- 结果页模板补充筛选栏、分页栏与当前区间提示，继续沿用正式任务明细接口。
- 接口样例与结果页字段说明同步更新到数据库基线实现。

## 涉及文件

- `custom_addons/logistics_web/services/waybill_standard_import_service_v2.py`
- `custom_addons/logistics_web/controllers/logistics_web_import_v3.py`
- `custom_addons/logistics_web/static/src/js/actions/import_result_action.js`
- `custom_addons/logistics_web/static/src/xml/import_result_templates.xml`
- `custom_addons/logistics_web/static/src/scss/import_pages.scss`
- `前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-23_四期导入接口返回样例.md`
- `前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-23_四期导入结果页字段说明.md`

## 验证关注点

- `logistics_web.import_result` 的 action tag、JS registry、OWL template 和 manifest 资产声明保持一致。
- `?debug=assets` 下结果页应能继续命中：
  - `/api/admin/logistics/imports/tasks/{task_no}`
  - `/api/admin/logistics/imports/tasks/{task_no}/lines`
  - `/api/admin/logistics/imports/tasks/{task_no}/errors`
- 行结果切换状态筛选时，页码应自动回到第 1 页。
- 行结果区和错误区的上一页/下一页按钮应分别独立工作。
