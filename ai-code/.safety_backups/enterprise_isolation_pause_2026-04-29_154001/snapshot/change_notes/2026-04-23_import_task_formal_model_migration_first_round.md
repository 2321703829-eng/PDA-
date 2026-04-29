# 2026-04-23 导入任务正式模型迁移首轮落地

## 本次变更

- 标准主数据导入预校验阶段改为直接落库到正式模型：
  - `logistics.import.source.file`
  - `logistics.import.task`
  - `logistics.import.task.line`
  - `logistics.import.error.line`
- 标准正式导入确认改为优先以 `task_no` 为入口，旧 `import_batch_no / precheck_token` 仅保留兼容回退。
- 导入结果、行结果、错误明细、错误报告统一增加或收口到任务路由：
  - `/api/admin/logistics/imports/tasks/<task_no>`
  - `/api/admin/logistics/imports/tasks/<task_no>/lines`
  - `/api/admin/logistics/imports/tasks/<task_no>/errors`
  - `/api/admin/logistics/imports/tasks/<task_no>/error-report`
- 预校验返回补齐正式任务头信息、源文件信息和错误报告信息，任务结果补齐 `operator` 字段。

## 影响范围

- `custom_addons/logistics_web/services/waybill_standard_import_service_v2.py`
- `custom_addons/logistics_web/controllers/logistics_web_import_v3.py`
- `custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- `前端设计/四期前端优化设计/01_专题方案/2026-04-23_四期导入任务正式落库迁移方案.md`
- `前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-23_四期导入接口返回样例.md`

## 边界说明

- 本轮只完成标准主数据导入首轮迁移，图片包导入暂未切到正式任务链。
- 历史旧批次结果读取仍保留兼容，但新预校验任务不再继续写入 `logistics.import.batch`。
- 当前任务结果统计仍以 `waybill / customer_line / goods_line` 为准，未在首轮补齐 `order_line` 汇总字段。

## 验证

- Python AST 语法解析通过：
  - `custom_addons/logistics_web/services/waybill_standard_import_service_v2.py`
  - `custom_addons/logistics_web/controllers/logistics_web_import_v3.py`
- `import_center_action.js` 已完成 `node --check`
- 任务链关键字段与路由已做关键词回扫：
  - `task_no`
  - `precheck_token`
  - `logistics.import.batch`
  - `source_rows_json`

## 后续建议

- 让结果页直接消费 `/lines` 与 `/errors` 路由，形成真正的前端任务明细闭环。
- 评估图片包导入复用同一套正式任务链的落地顺序。
