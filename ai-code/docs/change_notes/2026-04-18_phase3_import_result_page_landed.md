# 2026-04-18 phase3 import result page landed

## Objective

落地三期承接的“导入结果页页面化”，把原本只停留在导入中心页内的结果区，补成可独立回看、可继续跳转的结果页。

## Outcome

完成后，运单标准导入链路变成：

1. 导入中心上传与预校验
2. 正式导入
3. 自动进入独立导入结果页
4. 从结果页继续刷新、下载错误报告、回到导入中心、进入运单列表

同时继续复用现有：

- `GET /api/admin/logistics/imports/waybill-standard/result`
- `GET /api/admin/logistics/imports/waybill-standard/error-report`

没有重开第二套导入结果接口体系。

## Change Notes

### 1. 结果接口补最小字段

更新：

- [waybill_standard_import_service_v2.py](/D:/Desktop/Odoo/custom_addons/logistics_web/services/waybill_standard_import_service_v2.py)

在现有 `getWaybillImportResult` payload 上补齐：

- `template_code`
- `template_version`
- `file_name`
- `total_row_count`
- `passed_row_count`
- `failed_row_count`
- `confirmed_at`
- `finished_at`

保持原有 `result` 路由和 `code: 0/1` 口径不变。

### 2. 新增独立导入结果页 action

新增：

- [import_result_action.js](/D:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/actions/import_result_action.js)
- [import_result_templates.xml](/D:/Desktop/Odoo/custom_addons/logistics_web/static/src/xml/import_result_templates.xml)

页面固定落成 5 块：

1. 结果头部
2. 结果摘要卡区
3. 文件与批次信息区
4. 后续动作区
5. 失败说明与错误报告区

### 3. 导入中心接入结果页跳转

更新：

- [import_center_action.js](/D:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/actions/import_center_action.js)
- [import_center_templates.xml](/D:/Desktop/Odoo/custom_addons/logistics_web/static/src/xml/import_center_templates.xml)

这次接上的行为：

- 正式导入成功后自动打开独立结果页
- 导入中心支持带 `import_batch_no` 回看结果
- 导入中心结果区补了 `查看结果页`

### 4. 动作注册与资产接线

更新：

- [logistics_action_registry.js](/D:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/actions/logistics_action_registry.js)
- [logistics_web_actions.xml](/D:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_actions.xml)
- [__manifest__.py](/D:/Desktop/Odoo/custom_addons/logistics_web/__manifest__.py)
- [logistics_web.scss](/D:/Desktop/Odoo/custom_addons/logistics_web/static/src/scss/logistics_web.scss)

新增 client action：

- `logistics_web.import_result`

## Boundary

这轮没有扩到：

- 导入历史中心
- 非运单对象导入结果页
- 为结果页新开 `detail/review` 专用接口
- 为运单列表补一套新的导入批次字段筛选体系

当前 `按导入批次继续核验` 保持为“带批次上下文打开运单列表”的最小闭环。

## Verify

建议至少验证：

1. 导入中心正式导入后会自动进入导入结果页
2. 结果页能展示新增补字段
3. `刷新结果 / 下载错误报告 / 进入运单列表 / 返回导入中心` 可正常执行
4. 导入中心通过 `import_batch_no` 回看结果不报错

## Next Suggestion

如果下一轮要继续补强结果追溯，再评估是否真的需要把 `import_batch_no` 反挂到运单模型与列表筛选，而不是在这轮页面化任务里顺手扩大范围。
