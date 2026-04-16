# 2026-04-15 导入导出体验与中文化优化

## 目标

针对物流后台当前导入导出链路，补一轮更贴近业务团队使用习惯的体验优化。

本轮主要解决：

- 列表页导入入口不够显性
- 导入字段更偏技术术语，不够业务化
- 标准导出在部分模型上仍有较多英文表头
- 导入页中 `Date Format` 被误显示为 `数据格式`

## 本次修改

### 1. 独立导入入口

在 `custom_addons/logistics_web` 中新增了列表页导入按钮增强：

- 新增 [list_import_button.js](/d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/components/list_import_button.js)
- 新增 [list_import_button.xml](/d:/Desktop/Odoo/custom_addons/logistics_web/static/src/xml/list_import_button.xml)

效果：

- 在波次、批次、运单、留痕事件、留痕证据、异常队列列表页顶部新增独立 `导入` 按钮
- 原齿轮菜单中的 `导入记录` 保留

### 2. 导入页中文修正

在 `custom_addons/logistics_web` 中新增了导入页文案补丁：

- 新增 [import_localization_patch.js](/d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/components/import_localization_patch.js)

效果：

- `Date Format:` 改为 `日期格式：`
- `Datetime Format:` 改为 `日期时间格式：`
- `Formatting` 区块标题在页面上改为 `导入格式`

### 3. 调度主线业务字段别名

在 `custom_addons/logistics_dispatch` 中为导入兼容导出和批量导入补了业务别名字段：

- [logistics_dispatch_wave.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_wave.py)
  - `wave_no`
- [logistics_dispatch_batch.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_batch.py)
  - `batch_no`
  - `wave_no`
- [logistics_dispatch_waybill.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py)
  - `waybill_no`
  - `batch_no`
  - `customer_no`
  - `customer_name`
  - `store_no`
  - `store_name`

效果：

- 导入字段匹配时可以直接使用更贴近业务的列名
- 导入兼容导出时，可以导出更偏业务字段代码的列名

### 4. 业务字段与页面中文化

同步收口了基础主数据和留痕主线的中英文混排：

- `logistics_base`
  - 客户号、门店号、员工编号、仓库物流信息等标题改为中文
- `logistics_dispatch`
  - 波次、批次、菜单和搜索文案改为中文
- `logistics_trace_core`
  - 留痕事件字段、状态、按钮和搜索文案改为中文
- `logistics_trace_evidence`
  - 证据字段、状态、分组与页面标题改为中文
- `logistics_trace_exception`
  - 异常类型、状态、按钮、帮助文案和关联跳转标题改为中文

## 验证

已完成：

- 对新增 Python 代码做源码级语法检查，通过
- 核对导入页原生实现，确认日期格式与日期时间格式并非重复定义，而是原中文翻译不准确

未完成：

- 未在浏览器中做升级后的人工点验
- 未做 Odoo 服务重启后的真实页面截图回归

## 升级建议

建议升级模块：

- `logistics_base`
- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`
- `logistics_web`
