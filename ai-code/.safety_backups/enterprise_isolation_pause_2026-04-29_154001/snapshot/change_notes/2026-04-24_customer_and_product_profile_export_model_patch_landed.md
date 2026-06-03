# 2026-04-24 客户画像与货物画像导出模型补丁首轮落地

## This round

- 落地 `CPPR-EXP-M1` 的第一步：补齐客户画像与货物画像导出所需的模型枚举、结构化统计字段和迁移索引。
- 为后续 `from_customer / from_product` 服务层实现准备正式模型底座。

## Changed files

- `custom_addons/logistics_dispatch/models/selection_options.py`
- `custom_addons/logistics_dispatch/models/logistics_export_log.py`
- `custom_addons/logistics_dispatch/migrations/19.0.1.1.0/post-migration.py`

## What changed

- 扩展导出对象类型枚举：
  - `customer_profile`
  - `product_profile`
- 扩展导出入口类型枚举：
  - `from_product`
- 扩展导出包结构枚举：
  - `customer_profile_bundle_v1 / v2`
  - `product_profile_bundle_v1 / v2`
- 扩展导出目标对象类型枚举：
  - `partner`
  - `product`
- 在导出任务头新增通用结构化统计字段：
  - `package_metrics_json`
- 在导出任务行新增通用结构化统计字段：
  - `line_metrics_json`
- 在迁移脚本中补充索引：
  - `idx_export_task_object_entry_status`
  - `idx_export_task_line_target_object`

## Verify

- 使用 Python `ast.parse` 通过以下文件的语法校验：
  - [selection_options.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/selection_options.py:1)
  - [logistics_export_log.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_export_log.py:1)
  - [post-migration.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/migrations/19.0.1.1.0/post-migration.py:1)

## Next

- 继续做 `CP-EXP-S1`，先把 `from_customer` 的客户画像导出服务主链接起来
