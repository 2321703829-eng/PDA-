# 2026-04-16 标准模板双版本与界面入口切换
## Objective

把标准运单导入模板从单一英文列头版本，扩展为中英双版本下载，并把运单页面中的旧标准模板入口切换到新标准导入链路。

## Outcome

本次完成后：

1. 标准模板下载支持 `en_US` 与 `zh_CN` 两个版本
2. 新增中文列头模板文件 `TSL-IMPORT-WAYBILL-V1.zh_CN.csv`
3. `GET /api/admin/logistics/imports/waybill-standard/template` 返回双版本模板信息
4. `GET /api/admin/logistics/imports/waybill-standard/template/download` 支持 `template_locale`
5. 运单页面模板入口不再指向旧的 `运单标准导入模板.csv`，而是切到双版本标准模板下载地址

## Behavior

### 1. 双版本标准模板

当前支持：

- `en_US`：`TSL-IMPORT-WAYBILL-V1.csv`
- `zh_CN`：`TSL-IMPORT-WAYBILL-V1.zh_CN.csv`

两个版本仅列头语言不同，字段语义与导入链路完全一致。

### 2. 下载接口参数

标准模板下载接口新增：

- `template_locale`

当前允许值：

- `en_US`
- `zh_CN`

默认值：

- `en_US`

### 3. 页面入口切换策略

当前只替换“运单标准模板”入口：

- 原入口：旧的静态文件 `运单标准导入模板.csv`
- 新入口：标准模板（英文列头）/ 标准模板（中文列头）

客户明细模板与货物明细模板暂时保留旧入口，因为它们仍对应旧的分模型导入链路。

## Boundary

本次未包含：

1. 客户明细模板与货物明细模板的双版本化
2. 导入中心页面的独立模板选择页
3. 根据用户语言自动切换默认模板版本

## Files

- [TSL-IMPORT-WAYBILL-V1.zh_CN.csv](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/static/src/import_templates/TSL-IMPORT-WAYBILL-V1.zh_CN.csv)
- [logistics_dispatch_waybill.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py)
- [logistics_dispatch_import_support.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_import_support.py)
- [waybill_standard_import_service.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/waybill_standard_import_service.py)
- [logistics_web_import_v3.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/logistics_web_import_v3.py)
- [标准订单导入模板字段说明与错误反馈规范.md](/d:/Desktop/Odoo/ai-code/前端设计/二期前端优化设计/02_跨模块规范/01_接口与数据/标准订单导入模板字段说明与错误反馈规范.md)
- [前端接口设计总文档.md](/d:/Desktop/Odoo/ai-code/前端设计/二期前端优化设计/02_跨模块规范/01_接口与数据/前端接口设计总文档.md)

## Verify

本次已完成这些验证：

1. 相关 Python 文件 AST 解析通过
2. `logistics_dispatch, logistics_web` 模块升级成功
3. 服务层校验通过：
   - `build_template_payload()` 返回双版本模板信息
   - `load_template_bytes(template_locale='en_US')` 返回英文列头
   - `load_template_bytes(template_locale='zh_CN')` 返回中文列头
4. 运单页面模板入口校验通过：
   - 返回 `下载标准模板（英文列头）`
   - 返回 `下载标准模板（中文列头）`
   - 客户明细/货物明细模板入口仍保留

## Risk

当前仍有一个旧问题未在本次顺手处理：

1. `logistics_web_dashboard.py` 还在使用 `@route(type='json')`
   - Odoo 19 会给出 deprecated warning
   - 不影响本次标准模板双版本能力

## Next Suggestion

下一步建议继续把导入入口体验做完整：

1. 在导入页面显式增加“标准模板（英文列头）/ 标准模板（中文列头）”按钮
2. 再决定是否把客户明细与货物明细模板也迁移到新标准链路
