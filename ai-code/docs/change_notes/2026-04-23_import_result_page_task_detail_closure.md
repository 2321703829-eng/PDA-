# 2026-04-23 导入结果页接入任务行结果与错误明细

## 本次变更

- 结果页前端动作改为在读取任务头之外，继续直接消费：
  - `/api/admin/logistics/imports/tasks/<task_no>/lines`
  - `/api/admin/logistics/imports/tasks/<task_no>/errors`
- `import_result_action.js` 新增任务行结果、字段错误明细、明细加载异常和明细数量展示逻辑。
- `import_result_templates.xml` 从“摘要页”扩展为“摘要 + 行结果 + 错误明细”闭环页面。
- 同步更新结果页字段说明文档，冻结当前页面结构与字段口径。

## 影响范围

- `custom_addons/logistics_web/static/src/js/actions/import_result_action.js`
- `custom_addons/logistics_web/static/src/xml/import_result_templates.xml`
- `前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-23_四期导入结果页字段说明.md`

## 边界说明

- 首轮结果页只读取第一页明细：
  - 行结果 `page_size = 20`
  - 错误明细 `page_size = 20`
- 本轮不在结果页内继续做分页、筛选或搜索交互。
- 本轮不改动导入中心和后端任务接口结构。

## 验证

- `import_result_action.js` 已通过 `node --check`
- `import_result_templates.xml` 已通过 XML 解析
- 源链已复核：
  - `ir.actions.client tag = logistics_web.import_result`
  - JS registry key = `logistics_web.import_result`
  - component template = `logistics_web.ImportResultAction`
  - XML `t-name` = `logistics_web.ImportResultAction`
  - JS/XML 均已在 `web.assets_backend` 中声明

## 后续建议

- 若结果页后续要承接更大任务量，优先补任务行与错误明细分页。
- 若用户常用“按失败行重查”，可在下一轮补状态筛选与错误码聚合卡片。
