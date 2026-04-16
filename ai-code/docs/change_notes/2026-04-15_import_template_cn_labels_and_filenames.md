# 2026-04-15 导入模板中文文案与文件名收口

## 本次变更

- 将客户明细导入、货物明细导入页上的模板下载按钮文案改为中文：
  - `下载客户明细模板`
  - `下载货物明细模板`
- 将运单、客户明细、货物明细三类标准模板的下载路径切换为中文文件名：
  - `运单标准导入模板.csv`
  - `运单客户明细导入模板.csv`
  - `运单货物明细导入模板.csv`
- 新增中文模板内容，模板列头和样例值改为更贴近业务习惯的中文表达。
- 为客户明细、货物明细中文列头补充 `base_import.mapping` 预置映射，确保中文模板回传时仍可自动匹配到正确字段。

## 涉及文件

- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_line_v2.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_goods_line_v2.py`
- `custom_addons/logistics_dispatch/static/src/import_templates/运单标准导入模板.csv`
- `custom_addons/logistics_dispatch/static/src/import_templates/运单客户明细导入模板.csv`
- `custom_addons/logistics_dispatch/static/src/import_templates/运单货物明细导入模板.csv`
- `custom_addons/logistics_web/data/base_import_mapping_data.xml`

## 说明

- 旧的英文模板文件暂时保留，仅作为兼容路径，不再作为界面主下载入口。
- 本次未改动 Odoo 原生导入页结构，只收口了按钮文案、下载文件名、模板列头和对应映射。
