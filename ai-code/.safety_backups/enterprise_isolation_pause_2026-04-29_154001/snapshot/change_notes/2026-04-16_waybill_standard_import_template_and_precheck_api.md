# 2026-04-16 标准运单导入模板下载与预校验接口落地

## Objective

把二期导入链路里的 P1 能力先落地成可调用接口：

1. 标准模板元信息与下载入口
2. 标准模板预校验入口
3. 运单/客户/货物三层主路径的基础规则校验

## Outcome

本次完成后，系统已经具备下面这组可运行能力：

1. `GET /api/admin/logistics/imports/waybill-standard/template`
2. `GET /api/admin/logistics/imports/waybill-standard/template/download`
3. `POST /api/admin/logistics/imports/waybill-standard/precheck`
4. 单文件标准模板 `TSL-IMPORT-WAYBILL-V1.csv`

## Behavior

### 1. 模板下载

- 新增单文件标准模板：
  - `row_no`
  - `import_batch_mark`
  - `waybill_no`
  - `batch_no`
  - `wave_no`
  - `delivery_date`
  - `customer_no`
  - `customer_name`
  - `store_no`
  - `store_name`
  - `delivery_remark`
  - `goods_code`
  - `goods_name`
  - `spec`
  - `qty`
  - `package_count`
  - `uom_name`
  - `weight`
  - `volume`
  - `temperature_zone`
  - `package_type`
  - `remark`
- 元信息接口返回 `template_code / template_version / file_name / download_url / expected_fields`
- 下载接口当前返回 `CSV` 文件流

### 2. 预校验

预校验支持两种文件提交方式：

1. `multipart/form-data` 上传 `file`
2. 传 `file_base64`

当前已覆盖的规则：

1. 模板编码与列头校验
2. 必填校验：
   - `waybill_no`
   - `customer_no`
   - `goods_name`
   - `qty`
3. 格式校验：
   - `delivery_date` 必须是 `YYYY-MM-DD`
   - `qty > 0`
   - `package_count >= 0`
   - `weight >= 0`
   - `volume >= 0`
   - `temperature_zone` 必须在 `ambient / chilled / frozen / other`
4. 主数据匹配：
   - `batch_no`
   - `wave_no`
   - `customer_no`
   - `store_no`
5. 分组一致性：
   - 同一 `waybill_no` 下 `batch_no / wave_no / delivery_date` 必须一致
   - 同一 `waybill_no + customer_no` 下 `customer_name / store_no / store_name / delivery_remark` 必须一致
6. 客户与门店归属一致性：
   - 若门店存在父客户，则必须和 `customer_no` 对应客户一致

### 3. 返回结构

预校验接口当前返回：

- `precheck_token`
- `total_row_count`
- `passed_row_count`
- `failed_row_count`
- `can_confirm_import`
- `errors[]`

错误明细结构为：

```json
{
  "row_no": 2,
  "field_code": "customer_no",
  "field_label": "客户编号",
  "error_code": "CUSTOMER_NO_NOT_FOUND",
  "error_message": "客户编号不存在，请先维护客户主数据。"
}
```

## Boundary

本次明确不包含：

1. `confirmWaybillStandardImport`
2. `getWaybillImportResult`
3. `logistics_import_batch` 持久化模型
4. `precheck_token` 持久化复用
5. Excel `xlsx` 解析

因此当前 `precheck_token` 仅用于对齐返回结构，不承担后续导入确认功能。

## Files

- [TSL-IMPORT-WAYBILL-V1.csv](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/static/src/import_templates/TSL-IMPORT-WAYBILL-V1.csv)
- [import_service.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/import_service.py)
- [logistics_web_import_v2.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/logistics_web_import_v2.py)
- [controllers/__init__.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/__init__.py)

## Verify

已完成以下验证：

1. `logistics_web` 模块升级成功
2. 路由已注册：
   - `/api/admin/logistics/imports/waybill-standard/template`
   - `/api/admin/logistics/imports/waybill-standard/template/download`
   - `/api/admin/logistics/imports/waybill-standard/precheck`
3. 模板元信息返回：
   - 文件名 `TSL-IMPORT-WAYBILL-V1.csv`
   - `expected_fields` 共 `22` 个
4. 预校验通过样例：
   - `can_confirm_import = True`
   - `total_row_count = 1`
   - `passed_row_count = 1`
   - `failed_row_count = 0`
5. 预校验失败样例：
   - `can_confirm_import = False`
   - `total_row_count = 2`
   - `failed_row_count = 2`
   - 返回了 `BATCH_NO_NOT_FOUND / CUSTOMER_NO_NOT_FOUND / FIELD_FORMAT_INVALID / FIELD_VALUE_INVALID` 等细粒度错误

## Next Suggestion

下一步建议直接进入 P2：

1. 增加 `logistics_import_batch` 模型
2. 落 `confirmWaybillStandardImport`
3. 落 `getWaybillImportResult`
4. 把当前 `precheck_token` 从临时返回值升级为可确认导入的持久化令牌
