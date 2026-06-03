# 2026-04-24 司机侧 Excel 导出与默认波次补齐运行态验证

## Objective

- 升级 `logistics_dispatch` 与 `logistics_web` 模块。
- 跑一次真实 `delivery_date` 司机侧 Excel 导出 smoke。
- 验证四 Sheet 正式导入在缺失 `wave_no`、缺失 `delivery_date` 时，会自动补默认波次和有效配送日期。

## Runtime Verify

- 已执行模块升级：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init`
- 升级成功，最新服务代码已进入本地数据库 `odoo_logistics_phase4_v1` 运行态。

### 1. delivery_date 导出 smoke

- 验证日期：`2026-04-23`
- 导出文件：
  - [driver_route_export_smoke_2026-04-23.xlsx](</d:/Desktop/Odoo/ai-code/.smoke/driver_route_export_smoke_2026-04-23.xlsx>)
- 导出结果：
  - 工作表：`司机路线清单`
  - 数据行数：`7`
  - 表头为约定的 9 列：
    - `批次号`
    - `送货顺序`
    - `运单号`
    - `客户名称`
    - `门店名称`
    - `联系人`
    - `联系电话`
    - `地址`
    - `客户/门店备注`
  - 首行异常提醒为：
    - `导出日期：2026-04-23；异常提醒：本表包含 3 条需人工复查的停靠点，请重点检查 地址, 联系电话, 送货顺序。`

### 2. 默认波次补齐导入 smoke

- 烟测文件：
  - [auto_wave_import_smoke_20260424033827.xlsx](</d:/Desktop/Odoo/ai-code/.smoke/auto_wave_import_smoke_20260424033827.xlsx>)
- 烟测摘要：
  - [auto_wave_import_smoke_20260424033827.json](</d:/Desktop/Odoo/ai-code/.smoke/auto_wave_import_smoke_20260424033827.json>)
- 导入方式：
  - 使用四 Sheet 正式模板
  - 刻意留空 `wave_no`
  - 刻意留空 `delivery_date`
- 预校验任务：
  - `IMT260424-00013`
- 正式导入结果：
  - `status = success`
- 运行态验证结果：
  - 自动生成波次号：`AUTO-WV-20260424-001`
  - 生成规则命中：`AUTO-WV-YYYYMMDD-001`
  - 运单最终 `delivery_date = 2026-04-24`
  - 说明缺失配送日期时，已按导入任务创建日补齐

## Later Fix

- 后续已修复 `zh_CN` 四 Sheet 模板头与解析别名不一致的问题。
- 修复方式：
  - 在 [waybill_standard_import_service_v2.py](</d:/Desktop/Odoo/custom_addons/logistics_web/services/waybill_standard_import_service_v2.py>) 中新增统一的表头别名组装逻辑
  - 解析时不再只依赖历史 `FIELD_ALIASES`
  - 会始终把当前 `FIELD_LABELS` 中的正式中文字段名纳入合法匹配别名

## zh_CN Runtime Re-Verify

- 复验文件：
  - [zh_cn_template_import_smoke_20260424034156.xlsx](</d:/Desktop/Odoo/ai-code/.smoke/zh_cn_template_import_smoke_20260424034156.xlsx>)
- 复验摘要：
  - [zh_cn_template_import_smoke_20260424034156.json](</d:/Desktop/Odoo/ai-code/.smoke/zh_cn_template_import_smoke_20260424034156.json>)
- 预校验任务：
  - `IMT260424-00014`
- 正式导入结果：
  - `status = success`
- 复验结论：
  - `zh_CN` 模板已可直接通过预校验
  - 正式导入已成功
  - 缺失 `wave_no` 时仍会自动补齐 `AUTO-WV-20260424-001`
  - 缺失 `delivery_date` 时仍会补齐为 `2026-04-24`

## Current Boundary

- 当前这条“中文四 Sheet 模板直接导入”问题已经收口，不再是阻塞项。

## Related Code

- [driver_route_excel_export_service.py](</d:/Desktop/Odoo/custom_addons/logistics_web/services/driver_route_excel_export_service.py>)
- [logistics_web_export.py](</d:/Desktop/Odoo/custom_addons/logistics_web/controllers/logistics_web_export.py>)
- [waybill_standard_import_service_v2.py](</d:/Desktop/Odoo/custom_addons/logistics_web/services/waybill_standard_import_service_v2.py>)
