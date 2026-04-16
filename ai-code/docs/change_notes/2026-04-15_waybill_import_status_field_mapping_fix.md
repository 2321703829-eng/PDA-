# 2026-04-15 运单导入状态字段自动匹配修复
## 问题现象

- 在运单标准导入模板中，以下列头未自动匹配到字段：
  - `exception_status`
  - `evidence_status`
  - `risk_level`

## 根因

- `custom_addons/logistics_web/data/base_import_mapping_data.xml`
  中缺少针对 `logistics.dispatch.waybill` 的这组预置映射。
- 因此导入页虽然能自动识别 `waybill_no`、`batch_no`、`delivery_date`、`state`、`route_seq`、`remark`，
  但对这 3 个状态类列头不会自动命中。

## 修复

- 为 `logistics.dispatch.waybill` 补充以下映射：
  - `exception_status` -> `exception_status`
  - `exception status` -> `exception_status`
  - `evidence_status` -> `evidence_status`
  - `evidence status` -> `evidence_status`
  - `risk_level` -> `risk_level`
  - `risk level` -> `risk_level`
  - `risk` -> `risk_level`

## 影响文件

- `custom_addons/logistics_web/data/base_import_mapping_data.xml`

