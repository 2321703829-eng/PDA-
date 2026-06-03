# 2026-04-24 司机侧路线导出双入口落地

## Objective

- 把司机侧路线 Excel 导出入口同时接到两个地方：
  - 导入中心统一入口
  - 批次页业务快捷入口

## Changed Code

- 更新 [import_center_action.js](</d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/actions/import_center_action.js>)
- 更新 [import_center_templates.xml](</d:/Desktop/Odoo/custom_addons/logistics_web/static/src/xml/import_center_templates.xml>)
- 新增 [logistics_dispatch_batch.py](</d:/Desktop/Odoo/custom_addons/logistics_web/models/logistics_dispatch_batch.py>)
- 新增 [logistics_web_batch_views.xml](</d:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_batch_views.xml>)
- 更新 [__manifest__.py](</d:/Desktop/Odoo/custom_addons/logistics_web/__manifest__.py>)
- 更新 [四期司机侧Excel导出模块设计方案](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-24_四期司机侧Excel导出模块设计方案.md>)

## Summary

- 导入中心新增 `司机侧路线导出` 区块。
- 区块内按 `delivery_date` 直接发起司机路线 Excel 下载。
- 批次页新增 `司机路线导出` 按钮。
- 批次页按钮会跳到导入中心，并尽量根据当前批次自动预填导出日期。
- 两个入口最终统一走：
  - `POST /api/admin/logistics/exports/driver-route-excel/direct-download`

## Verify

- `import_center_action.js` 已通过 `node --check`
- `import_center_templates.xml` 与 `logistics_web_batch_views.xml` 已通过 XML 解析
- `logistics_dispatch_batch.py` 已通过 Python AST 校验

## Boundary

- 本轮只完成入口落位，不新增独立“司机导出中心”
- 批次页入口是“带上下文跳转到统一入口”，不是在批次页内直接下载
