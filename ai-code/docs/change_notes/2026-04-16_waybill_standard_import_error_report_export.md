# 2026-04-16 标准运单导入错误报告导出
## Objective

在已完成 `template / precheck / confirm / result` 闭环的基础上，继续把导入体验收口：

1. 让预校验失败后可以直接下载错误报告
2. 让 `precheck` 和 `result` 返回可直接访问的 `error_report_url`
3. 给标准运单导入链路补一个稳定的错误报告下载接口

## Outcome

本次完成后，标准运单导入新增一个错误报告下载能力：

- `GET /api/admin/logistics/imports/waybill-standard/error-report`

同时：

1. `precheck` 返回中新增 `import_batch_no`
2. `precheck` 返回中新增 `error_report_url`
3. `result` 返回继续透出 `error_report_url`
4. 失败批次可通过 `import_batch_no` 或 `precheck_token` 下载错误报告

## Behavior

### 1. 预校验回填批次号和错误报告地址

`precheck` 在落库 `logistics.import.batch` 后：

1. 回填 `import_batch_no = batch.name`
2. 当存在错误时，生成：
   - `error_report_url = /api/admin/logistics/imports/waybill-standard/error-report?import_batch_no=...`
3. 把该地址同时写入批次字段 `error_report_url`

### 2. 错误报告下载接口

新增接口：

- `GET /api/admin/logistics/imports/waybill-standard/error-report`

支持两种查询方式：

1. `import_batch_no`
2. `precheck_token`

优先按 `import_batch_no` 查找，查不到再按 `precheck_token` 查找。

### 3. 错误报告文件格式

当前错误报告导出为 `CSV`，文件名格式为：

- `{import_batch_no}-error-report.csv`

列头固定为：

1. `行号`
2. `字段编码`
3. `字段名称`
4. `错误编码`
5. `错误说明`

编码使用 `UTF-8 with BOM`，方便 Excel 直接打开。

## Boundary

本次仍未包含：

1. `xlsx` 错误报告导出
2. 页面内导入结果页按钮联动
3. 正式导入运行期异常的结构化错误报告
4. 错误报告长期归档或附件化

## Files

- [waybill_standard_import_service.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/waybill_standard_import_service.py)
- [logistics_web_import_v3.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/logistics_web_import_v3.py)

## Verify

本次已完成这些验证：

1. `waybill_standard_import_service.py` 与 `logistics_web_import_v3.py` AST 解析通过
2. `logistics_dispatch, logistics_web` 模块升级成功
3. 失败样例预校验通过服务层验证：
   - `precheck.can_confirm_import = false`
   - 返回了 `import_batch_no`
   - 返回了 `error_report_url`
4. 错误报告导出通过服务层验证：
   - 导出文件名为 `{import_batch_no}-error-report.csv`
   - 导出内容包含 `CUSTOMER_NO_NOT_FOUND / FIELD_FORMAT_INVALID / FIELD_ENUM_INVALID` 等错误

## Risk

当前仍有一个旧问题未在本次顺手处理：

1. `logistics_web_dashboard.py` 还在使用 `@route(type='json')`
   - Odoo 19 会给出 deprecated warning
   - 不影响本次错误报告导出能力

## Next Suggestion

下一步建议继续做导入体验层补齐：

1. 补一份可直接联调的 Postman / Apifox 示例
2. 如果你准备做页面联动，可以继续把导入结果页与错误报告下载按钮接到前端入口
