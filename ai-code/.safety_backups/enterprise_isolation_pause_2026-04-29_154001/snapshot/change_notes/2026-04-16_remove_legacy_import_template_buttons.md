# 2026-04-16 移除旧模板下载按钮并统一到标准模板
## Objective

把运单、客户明细、货物明细页面上的旧模板下载按钮全部撤掉，统一只保留标准模板下载入口，避免继续引导用户走旧的分模型模板思路。

## Outcome

本次完成后：

1. `logistics.dispatch.waybill` 只返回两类模板按钮：
   - `下载标准模板（英文列头）`
   - `下载标准模板（中文列头）`
2. `logistics.dispatch.waybill.customer.line` 只返回同样两类标准模板按钮
3. `logistics.dispatch.waybill.customer.goods.line` 只返回同样两类标准模板按钮
4. 页面上不再暴露：
   - `下载客户明细模板`
   - `下载货物明细模板`
   - 旧的 `下载运单标准模板`

## Behavior

### 1. 页面入口统一

三个业务页面统一下载同一份标准模板：

- 英文列头：`TSL-IMPORT-WAYBILL-V1.csv`
- 中文列头：`TSL-IMPORT-WAYBILL-V1.zh_CN.csv`

### 2. 旧模板处理方式

本次移除的是“页面上的旧模板按钮”，不再让用户从界面进入旧模板路径。

旧静态模板文件当前仍保留在仓库中，作为历史文件存在，但已经不再作为当前页面入口暴露。

## Boundary

本次未包含：

1. 物理删除仓库中的旧模板静态文件
2. 清理历史文档中对旧模板文件名的引用
3. 重构旧的分模型导入逻辑本身

## Files

- [logistics_dispatch_waybill.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py)
- [logistics_dispatch_import_support.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_import_support.py)
- [logistics_dispatch_waybill_customer_line_v2.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_line_v2.py)
- [logistics_dispatch_waybill_customer_goods_line_v2.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_goods_line_v2.py)

## Verify

本次已完成这些验证：

1. 相关 Python 文件 AST 解析通过
2. `logistics_dispatch, logistics_web` 模块升级成功
3. 运行态方法抽检通过：
   - `logistics.dispatch.waybill.get_import_templates()`
   - `logistics.dispatch.waybill.customer.line.get_import_templates()`
   - `logistics.dispatch.waybill.customer.goods.line.get_import_templates()`
4. 三个模型当前都只返回：
   - `下载标准模板（英文列头）`
   - `下载标准模板（中文列头）`

## Risk

当前仍有一个旧问题未在本次顺手处理：

1. `logistics_web_dashboard.py` 还在使用 `@route(type='json')`
   - Odoo 19 会给出 deprecated warning
   - 不影响本次模板按钮收口

## Next Suggestion

下一步如果你确认旧模板彻底不需要了，可以继续做两件事：

1. 物理删除仓库中的旧模板静态文件
2. 清理设计文档和历史说明里对旧模板文件名的残留引用
