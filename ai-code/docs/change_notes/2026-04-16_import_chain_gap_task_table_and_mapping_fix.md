# 2026-04-16 导入链路缺口任务表与异常/留痕映射补齐

## Objective

把当前二期导入链路的“已完成 / 未完成”拆成可执行任务表，并优先补齐第 1 个明显缺口：异常与留痕对象的表头自动匹配。

## Current Status

当前仓库里，导入相关能力已经落到下面这几层：

1. 已有独立 `导入` 按钮，能从列表页直接进入 Odoo 原生导入页
2. 已有波次、批次、运单、客户明细、货物明细的业务别名字段与部分表头映射
3. 已有三层对象：
   - 运单
   - 客户明细
   - 货物明细
4. 已有三份模板资源：
   - 运单标准导入模板
   - 运单客户明细导入模板
   - 运单货物明细导入模板

但下面这些仍未落地：

1. 标准模板下载接口
2. 预校验接口
3. 正式导入确认接口
4. 导入结果页接口
5. 导入批次模型、`precheck_token`、结果持久化
6. 单文件标准模板版本化主路径

## Task Table

| 优先级 | 任务 | 目标 | 当前状态 | 建议落位 |
| --- | --- | --- | --- | --- |
| P0 | 补异常与留痕表头映射 | 通过英文/中文表头自动匹配异常与留痕字段 | 本次已完成 | `logistics_web/data/base_import_mapping_data.xml` |
| P1 | 模板下载接口 | 从标准导入主路径下载模板，而不是手工找静态文件 | 未开始 | `logistics_web/controllers/logistics_web_import.py` |
| P1 | 标准导入预校验 | 上传文件后返回文件级、行级、字段级错误 | 未开始 | `logistics_web/controllers/logistics_web_import.py` + `logistics_web/services/import_service.py` |
| P2 | 正式导入确认 | 预校验通过后再正式落库，禁止绕过预校验 | 未开始 | `logistics_web/controllers/logistics_web_import.py` + `logistics_web/services/import_service.py` |
| P2 | 导入结果页 | 返回导入批次、成功/失败数、错误清单、回跳对象 | 未开始 | `logistics_web/controllers/logistics_web_import.py` + `logistics_dispatch/models/logistics_import_batch.py` |
| P2 | 导入批次模型 | 持久化 `precheck_token / import_batch_no / 结果摘要` | 未开始 | `logistics_dispatch/models/logistics_import_batch.py` |
| P2 | 单文件标准模板 V1 | 用一份版本化模板承接“运单 -> 客户 -> 货物”主路径 | 未开始 | `logistics_dispatch/static/src/import_templates/` |

## This Change

本次先完成 P0：

1. 为 `logistics.trace.event` 补充英文/中文表头映射：
   - `trace event`
   - `event type`
   - `object type`
   - `trace time`
   - `waybill`
   - `batch`
   - `submit source`
   - `备注`
2. 为 `logistics.trace.exception` 补充英文/中文表头映射：
   - `Exception No`
   - `Exception Type`
   - `Severity`
   - `Waybill`
   - `Batch`
   - `Trace Event`
   - `Process Owner Name`
   - `Report Time`
   - `异常单号`
   - `处理负责人姓名`

## Files

- [base_import_mapping_data.xml](/d:/Desktop/Odoo/custom_addons/logistics_web/data/base_import_mapping_data.xml)

## Verify

计划验证以下结果：

1. `logistics.trace.exception` 已存在新的 `base_import.mapping`
2. `logistics.trace.event` 已存在新的 `base_import.mapping`
3. 异常导入表头 `Exception Type / Severity / Trace Event / Process Owner Name` 可被映射到正确字段
4. 留痕导入表头 `Trace Event / Event Type / Trace Time` 可被映射到正确字段

## Next Suggestion

下一步建议直接进入 P1：

1. 先补 `downloadWaybillStandardTemplate`
2. 再补 `precheckWaybillStandardImport`
3. 预校验稳定后，再推进 `confirmWaybillStandardImport` 和 `getWaybillImportResult`
