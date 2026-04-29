# 2026-04-16 V2 三 Sheet 标准导入落地

## 本次目标

把 [2026-04-16_TSL-IMPORT-WAYBILL-V2三Sheet标准模板正式规格.md](../../前端设计/二期前端优化设计/00_导航与总纲/2026-04-16_TSL-IMPORT-WAYBILL-V2三Sheet标准模板正式规格.md) 落地为当前运行中的标准导入链路，完成从 `V1 CSV` 到 `V2 XLSX` 的主路径切换。

## 本次变更

### 1. 标准模板升级为 V2

- 新标准模板编码切换为 `TSL-IMPORT-WAYBILL-V2`
- 新标准模板版本切换为 `v2`
- 标准模板文件切换为：
  - `TSL-IMPORT-WAYBILL-V2.xlsx`
  - `TSL-IMPORT-WAYBILL-V2.zh_CN.xlsx`
- 模板内固定包含 3 个业务 Sheet：
  - `运单`
  - `客户明细`
  - `货物明细`

### 2. 导入服务切换到三 Sheet XLSX 实现

新增服务文件：

- `custom_addons/logistics_web/services/waybill_standard_import_service_v2.py`

当前服务能力：

- 生成中英双版本 V2 模板
- 解析 `.xlsx` 工作簿
- 校验 Sheet 结构与列头
- 执行跨 Sheet 预校验
- 执行正式导入
- 查询导入结果
- 导出预校验错误报告

### 3. 导入控制器切换到 V2

更新文件：

- `custom_addons/logistics_web/controllers/logistics_web_import_v3.py`

当前生效接口：

- `/api/admin/logistics/imports/waybill-standard/template`
- `/api/admin/logistics/imports/waybill-standard/template/download`
- `/api/admin/logistics/imports/waybill-standard/precheck`
- `/api/admin/logistics/imports/waybill-standard/confirm`
- `/api/admin/logistics/imports/waybill-standard/result`
- `/api/admin/logistics/imports/waybill-standard/error-report`

当前下载返回类型：

- 标准模板下载：`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- 错误报告下载：`text/csv; charset=utf-8`

### 4. 页面模板入口切换为 V2

更新文件：

- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_import_support.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_line_v2.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_goods_line_v2.py`

当前页面模板按钮统一为：

- `下载标准模板（英文列头）`
- `下载标准模板（中文列头）`

旧模板按钮已从页面入口移除。

### 5. 客户层字段补齐

更新文件：

- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_line_v2.py`

新增字段：

- `customer_ref`

用于承接 `客户明细` Sheet 中的 `customer_ref` 列。

## 运行态验证

### 已完成验证

1. 模块升级成功
   - 已执行：
     - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_dispatch,logistics_web --stop-after-init`

2. 语法校验通过
   - V2 service、controller、waybill/customer/goods import support 相关文件 AST 校验通过

3. 成功路径验证通过
   - 使用 `zh_CN` 版本 V2 模板构造三 Sheet 样例
   - `precheck` 返回：
     - `can_confirm_import = true`
     - `failed_row_count = 0`
   - `confirm` 返回：
     - `status = finished`
     - `created_waybill_count = 1`
     - `created_customer_line_count = 1`
     - `created_goods_line_count = 1`
   - `result` 返回：
     - `status = finished`
   - 数据已成功落库到运单、客户明细、货物明细

4. 失败路径验证通过
   - 使用“客户明细 Sheet 为空”的失败样例
   - `precheck` 返回：
     - `can_confirm_import = false`
     - `failed_row_count = 1`
     - `error_codes` 包含 `TEMPLATE_SHEET_EMPTY`
   - `error-report` 可正常导出
   - 错误报告已带 `Sheet` 列

### 本次顺手修复

在 V2 预校验汇总阶段，补了一个结构级错误统计修正：

- 当错误只发生在模板级或 Sheet 级，且没有具体数据行号时
- `failed_row_count` 不再错误地保持为 `0`
- `can_confirm_import` 也不会再被误判为 `true`

## 当前边界

- 当前主路径已切换到 `V2 XLSX`
- 当前错误报告仍为 `CSV`，未升级为 `XLSX`
- 当前 `V1 CSV` 文件与旧代码仍保留在仓库中，用于兼容和历史追溯，但不再作为界面主入口
- `客户与货品固定需求 / 临时需求拆分` 仍属于后续方向，不在本次范围内

## 下一步建议

1. 继续补一份面向联调的 Postman / Apifox 示例
2. 继续补页面侧的导入结果展示与错误报告下载交互
3. 再评估是否保留 `V1 CSV` 兼容链路，或在后续版本正式退役
