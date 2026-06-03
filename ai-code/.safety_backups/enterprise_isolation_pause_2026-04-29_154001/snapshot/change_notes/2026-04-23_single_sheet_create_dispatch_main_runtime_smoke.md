# 2026-04-23 single sheet create dispatch main runtime smoke

## Summary

- 在 `odoo_logistics_phase4_v1` 上完成了 `logistics_dispatch, logistics_web` 的模块升级。
- 重启本地 Odoo 后，对单表新建主链导入链做了真实运行态 smoke。
- smoke 覆盖了模板下载、预校验、正式导入、任务结果、行结果、错误明细、bundle 资产命中和动作页 HTTP 打开。

## Environment

- Database: `odoo_logistics_phase4_v1`
- Service URL: `http://127.0.0.1:8069`
- Auth user: `admin`
- Upgrade date: `2026-04-23`

## Upgrade

- Stopped the process listening on `127.0.0.1:8069`
- Ran:

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init
```

- Restarted:

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1
```

## Smoke Data

- Template: `TSL-IMPORT-WAYBILL-V3`
- Locale: `en_US`
- Real workbook path:
  - `D:\Desktop\Odoo\ai-code\.smoke\single_sheet_import_smoke_0423162714.xlsx`
- Result JSON path:
  - `D:\Desktop\Odoo\ai-code\.smoke\single_sheet_import_smoke_0423162714.json`

## Smoke Result

- Precheck task: `IMT260423-00005`
- Precheck:
  - `can_confirm_import = true`
  - `total_row_count = 3`
  - `passed_row_count = 3`
  - `failed_row_count = 0`
- Confirm import:
  - `status = success`
  - `created_wave_count = 1`
  - `created_batch_count = 1`
  - `created_waybill_count = 2`
  - `created_customer_line_count = 3`
  - `created_goods_line_count = 3`
- Task result:
  - `status = success`
  - `success_count = 3`
  - `fail_count = 0`
- Task lines:
  - `total = 3`
- Task errors:
  - `total = 0`

## Database Readback

- Wave created:
  - `SM-WV-0423162714`
- Batch created:
  - `SM-BT-0423162714`
- Waybills created:
  - `SM-WB-0423162714-01`
  - `SM-WB-0423162714-02`
- Customer lines created:
  - `SM-WB-0423162714-01-CL-001`
  - `SM-WB-0423162714-01-CL-002`
  - `SM-WB-0423162714-02-CL-001`

## Product / Asset Check

- `GET /web?debug=assets` returned `200`
- Real bundle grep succeeded in:
  - `/web/assets/debug/web.assets_backend.js`
  - `/web/assets/debug/web.assets_web.js`
- Verified bundle contains:
  - `logistics_web.import_center`
  - `logistics_web.ImportCenterAction`
  - `logistics_web.import_result`
  - `logistics_web.ImportResultAction`
- Verified action URLs return `200`:
  - `/odoo/action-logistics_web.action_logistics_web_import_center?debug=assets`
  - `/odoo/action-logistics_web.action_logistics_web_import_result?debug=assets`

## Notes

- A first failed smoke was caused by using the Chinese-header template while writing field-code keys directly, plus the built-in sample rows were not cleared. After switching to `en_US` headers and deleting sample rows, the smoke passed.
- Direct HTML inspection of `/web?debug=assets` did not list the import source files as plain static paths, but the real generated backend bundle did contain the action keys and template names.
