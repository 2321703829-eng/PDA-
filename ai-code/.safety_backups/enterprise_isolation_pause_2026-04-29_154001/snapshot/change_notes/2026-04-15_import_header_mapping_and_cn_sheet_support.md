# 2026-04-15 导入表头映射与中文表格适配补充

## 背景

在继续核验 [2026-04-15_Odoo物流后台导入导出体验优化方案](d:/Desktop/Odoo/ai-code/二期前端优化设计/2026-04-15_Odoo物流后台导入导出体验优化方案.md) 时，发现当前导入链路还有两类体验缺口：

- 旧英文表头与业务别名表头自动匹配不稳定，例如 `Batch`、`Exception Type`
- 异常模型的导入导出字段仍不够业务化，无法很好承接 `运单号 / 批次号 / 留痕事件` 这类业务列

## 本次调整

### 1. 预置物流模型的导入表头映射

文件：
- `custom_addons/logistics_web/data/base_import_mapping_data.xml`

调整：
- 预置了波次、批次、运单、留痕事件、留痕证据、异常的常见中英文表头映射
- 重点覆盖：
  - `Batch -> batch_no`
  - `Waybill -> waybill_no`
  - `Exception No -> exception_no`
  - `Exception Type -> exception_type`
  - `Severity -> severity_level`
  - `Trace Event -> trace_event_name`
- 同时补充中文业务表头映射，例如 `运单号 / 批次号 / 异常单号 / 处理负责人姓名`

### 2. 修正 base_import.mapping 的表头记忆稳定性

文件：
- `custom_addons/logistics_web/models/base_import_mapping.py`

调整：
- 对 `base_import.mapping` 做继承
- 新增保存时的 `column_name` 归一化逻辑：去首尾空格并转小写
- 这样像 `Batch`、`Exception No` 这类首字母大写表头，在成功导入一次后也能被后续导入稳定复用

### 3. 异常模型补充业务别名字段

文件：
- `custom_addons/logistics_trace_exception/models/logistics_trace_exception.py`

新增：
- `exception_no`
- `waybill_no`
- `batch_no`
- `trace_event_name`

补充能力：
- 支持用异常单号、运单号、批次号、留痕事件名称进行导入
- `process_owner_name` 现在也支持反向解析到处理负责人
- 对未找到或重名的关联对象，返回更明确的中文校验错误

## 中文表格适配结论

这轮排查确认：

1. 中文表头

- Odoo 原生支持按字段中文标题匹配
- 当前问题主要不是中文表头本身，而是业务团队常用表头和旧英文表头没有被预置映射

2. 中文值

- 选择字段支持技术值、英文标签和当前语言翻译值
- Many2one 字段支持按显示名称、外部 ID、数据库 ID 导入
- 因此像 `延迟 / 中 / 待处理` 这类中文值，本身是可适配的

3. 当前仍需注意的边界

- `Evidence Count`、`Overdue` 这类派生字段更偏结果字段，不建议作为主导入列
- 如果基础数据存在重名、重复编号或档案未建好，表头匹配成功后仍可能在导入阶段报关联错误

## 涉及模块

- `logistics_web`
- `logistics_trace_exception`

## 验证

已完成：
- Python 语法级校验应覆盖本次新增/修改的 Python 文件
- XML 数据文件已按 Odoo 标准 `record` 结构新增

待人工确认：
- 升级模块后，异常导入页中 `Batch / Exception Type / Severity / Trace Event / Process Owner Name` 是否能自动匹配
- 使用中文表头的 Excel/CSV 是否能直接命中业务字段
