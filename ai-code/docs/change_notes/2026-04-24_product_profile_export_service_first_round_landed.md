# 2026-04-24 from_product 货物画像导出服务首轮落地

## This round

- 落地 `PP-EXP-S1`，为货物画像导出接上首轮服务主链。
- 在不改 Controller 和前端入口的前提下，先让 `from_product` 具备任务创建、任务执行、结果查询、错误报告和主文件下载的服务能力。

## Changed files

- `custom_addons/logistics_web/services/product_profile_export_service.py`
- `custom_addons/logistics_web/services/__init__.py`

## What changed

- 新增 `ProductProfileExportService`
- 正式收口货物画像导出常量：
  - `object_type = product_profile`
  - `entry_type = from_product`
  - `package_structure = product_profile_bundle_v1`
  - `source_model = product.template`
  - `target_object_type = product`
- 实现首轮对外方法：
  - `create_product_profile_export_task`
  - `run_product_profile_export_task`
  - `get_export_task_result`
  - `get_export_task_lines`
  - `get_export_task_errors`
  - `build_export_task_error_report`
  - `get_export_download_file`
- 正式导出主文件首轮固定为两张 Sheet：
  - `ProductProfile`
  - `ProductUnit`
- 任务执行结果写入：
  - `package_metrics_json.product_count`
  - `package_metrics_json.product_unit_count`
  - `line_metrics_json.product_count`
  - `line_metrics_json.product_unit_count`
- 物理文件命名按货物画像导出口径收口为：
  - `TSL-EXPORT-PRODUCT-PROFILE-{timestamp}.xlsx`

## Boundary

- 首轮只从 `product.template` 读取货物主档字段。
- 首轮规格层只从 `logistics.product.unit` 展开。
- 首轮不接 `CustomerProductRelation`
- 首轮不从 `goods_line` 反推主档导出。

## Verify

- 使用 Python `ast.parse` 通过以下文件的语法校验：
  - [product_profile_export_service.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/product_profile_export_service.py:1)
  - [services/__init__.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/__init__.py:1)

## Next

- 继续做 `CPPR-EXP-C1`，把 `from_customer / from_product` 的创建路由接到正式导出 controller 上
