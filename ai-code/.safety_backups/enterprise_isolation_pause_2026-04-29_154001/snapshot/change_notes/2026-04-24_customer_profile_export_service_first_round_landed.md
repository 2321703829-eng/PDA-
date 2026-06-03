# 2026-04-24 from_customer 客户画像导出服务首轮落地

## This round

- 落地 `CP-EXP-S1`，为客户画像导出接上首轮服务主链。
- 在不改 Controller 和前端入口的前提下，先让 `from_customer` 具备任务创建、任务执行、结果查询、错误报告和主文件下载的服务能力。

## Changed files

- `custom_addons/logistics_web/services/customer_profile_export_service.py`
- `custom_addons/logistics_web/services/__init__.py`

## What changed

- 新增 `CustomerProfileExportService`
- 正式收口客户画像导出常量：
  - `object_type = customer_profile`
  - `entry_type = from_customer`
  - `package_structure = customer_profile_bundle_v1`
  - `source_model = res.partner`
  - `target_object_type = partner`
- 实现首轮对外方法：
  - `create_customer_profile_export_task`
  - `run_customer_profile_export_task`
  - `get_export_task_result`
  - `get_export_task_lines`
  - `get_export_task_errors`
  - `build_export_task_error_report`
  - `get_export_download_file`
- 正式导出主文件首轮固定为单 Sheet：
  - `CustomerProfile`
- 任务执行结果写入：
  - `package_metrics_json.customer_count`
  - `line_metrics_json.customer_count`
- 物理文件命名按客户画像导出口径收口为：
  - `TSL-EXPORT-CUSTOMER-PROFILE-{timestamp}.xlsx`

## Boundary

- 首轮只从 `res.partner` 读取统一客户画像字段。
- 首轮不接 `CustomerProductRelation`
- 首轮不从 `logistics.customer.profile / logistics.store.profile` 直接拼主文件。

## Verify

- 使用 Python `ast.parse` 通过以下文件的语法校验：
  - [customer_profile_export_service.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/customer_profile_export_service.py:1)
  - [services/__init__.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/__init__.py:1)

## Next

- 继续做 `PP-EXP-S1`，把 `from_product` 的货物画像导出服务主链接起来
