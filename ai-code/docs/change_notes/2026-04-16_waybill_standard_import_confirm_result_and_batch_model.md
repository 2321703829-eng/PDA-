# 2026-04-16 标准运单导入 confirm/result 与导入批次模型落地

## Objective

在已完成模板下载与预校验的基础上，把标准运单导入链路补成闭环：

1. 落地导入批次持久化模型
2. 落地正式导入确认接口
3. 落地导入结果查询接口

## Outcome

本次完成后，导入链路已具备完整闭环：

1. `GET /api/admin/logistics/imports/waybill-standard/template`
2. `GET /api/admin/logistics/imports/waybill-standard/template/download`
3. `POST /api/admin/logistics/imports/waybill-standard/precheck`
4. `POST /api/admin/logistics/imports/waybill-standard/confirm`
5. `GET /api/admin/logistics/imports/waybill-standard/result`

同时新增持久化模型：

- `logistics.import.batch`

## Behavior

### 1. 预校验持久化

预校验不再只返回临时 token，而是会创建一条 `logistics.import.batch` 记录，持久化：

- `precheck_token`
- `template_code`
- `template_version`
- `file_name`
- `file_checksum`
- `total_row_count`
- `passed_row_count`
- `failed_row_count`
- `can_confirm_import`
- `source_rows_json`
- `errors_json`
- `expires_at`

当前 `precheck_token` 有效期为 `24` 小时。

### 2. 正式导入确认

`confirm` 接口以 `precheck_token` 为入口，当前行为如下：

1. 只允许 `prechecked` 且 `can_confirm_import = true` 的批次进入正式导入
2. 若 token 过期，批次状态会转成 `expired`
3. 若同一个 token 已经导入完成，则直接返回已有导入结果
4. 当前导入是“创建型导入”：
   - 新增运单
   - 新增客户明细
   - 新增货物明细
5. 当前不做更新型导入，若预校验时发现 `waybill_no` 已存在，会直接报错阻断

### 3. 当前导入分层

导入确认时按三层创建：

1. 运单层：
   - 按 `waybill_no` 分组
   - 创建 `logistics.dispatch.waybill`
2. 客户层：
   - 按 `waybill_no + customer_no + store_no` 分组
   - 创建 `logistics.dispatch.waybill.customer.line`
3. 货物层：
   - 每一行明细创建一条 `logistics.dispatch.waybill.customer.goods.line`

### 4. 结果查询

`result` 接口按 `import_batch_no` 查询，当前返回：

- `import_batch_no`
- `status`
- `status_label`
- `created_waybill_count`
- `created_customer_line_count`
- `created_goods_line_count`
- `updated_record_count`
- `skipped_record_count`
- `failed_record_count`
- `error_report_url`
- `failure_reason`

## Boundary

本次仍未包含：

1. Excel `xlsx` 模板解析
2. 更新型导入
3. 错误报告文件下载
4. 批次结果管理页面

## Files

- [logistics_import_batch.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_import_batch.py)
- [ir.model.access.csv](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/security/ir.model.access.csv)
- [waybill_standard_import_service.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/waybill_standard_import_service.py)
- [logistics_web_import_v3.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/logistics_web_import_v3.py)
- [services/__init__.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/__init__.py)
- [controllers/__init__.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/__init__.py)
- [logistics_web/__init__.py](/d:/Desktop/Odoo/custom_addons/logistics_web/__init__.py)

## Verify

已完成这些验证：

1. `logistics_dispatch, logistics_web` 模块升级成功
2. 路由注册成功：
   - `/api/admin/logistics/imports/waybill-standard/confirm`
   - `/api/admin/logistics/imports/waybill-standard/result`
3. 在事务回滚环境里跑通闭环：
   - `precheck -> confirm -> result`
4. 闭环验证结果：
   - `precheck.can_confirm_import = true`
   - `confirm.status = finished`
   - `result.created_waybill_count = 1`
   - `result.created_customer_line_count = 1`
   - `result.created_goods_line_count = 1~2`
5. 实际创建记录验证通过：
   - 运单创建成功
   - 客户明细创建成功
   - 货物明细创建成功

## Risk

当前仍有一个旧问题没有在本次顺手处理：

1. `logistics_web_dashboard.py` 还在使用 `@route(type='json')`
   - Odoo 19 会给出 deprecated warning
   - 不影响本次导入链路功能

## Next Suggestion

下一步建议转到导入体验和运维收口：

1. 给导入链路补一份可直接用于联调的 Postman/Apifox 示例
2. 补 `error_report_url` 的错误导出能力
3. 视业务需要决定是否支持“已有运单更新型导入”
