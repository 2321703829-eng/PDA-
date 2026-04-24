# 2026-04-23 四 Sheet 运行态升级、Schema 校验与端到端 Smoke
## Objective

- 完成 `logistics_dispatch + logistics_web` 的本地模块升级。
- 验证本轮字段补齐后的数据库 schema 已实际生效。
- 以真实四 Sheet Excel 跑通 `precheck -> confirm -> task result/lines/errors -> 数据库回查`。

## Runtime Upgrade

- 执行：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init`
- 首次升级被旧视图阻塞：
  - `logistics_dispatch_waybill_views.xml` 仍引用 `partner_no / partner_name`
  - 对应模型 `logistics.dispatch.waybill.customer.goods.line` 缺少兼容字段
- 已补兼容字段：
  - `logistics_dispatch_waybill_customer_goods_line_v2.py`
  - 新增 `partner_no / partner_name` 及 compute/inverse 兼容逻辑
- 后续再次升级通过。

## Schema Verify

- `logistics_dispatch_batch` 已确认存在：
  - `driver_name_snapshot`
  - `driver_phone_snapshot`
  - `route_name_snapshot`
  - `warehouse_name_snapshot`
- `res_partner` 已确认存在并可写入：
  - `organization_name`
  - `department_name`
  - `salesperson_name`
  - `channel_name`
  - `customer_status`
  - `allow_cash_on_delivery`
  - `invoice_type`
  - `contact_phone`
  - `address_full`
  - `route_preference`
  - `warehouse_preference`
  - `receive_start_time / receive_end_time`
  - `delivery_week_flags`
  - `delivery_access_flags`
- `logistics_customer_profile / logistics_store_profile` 已确认存在并可承接客户画像与门店画像字段。

## Smoke Process

- 清理旧 `8069` 监听后，仅保留升级后的 Odoo 进程。
- 通过真实 HTTP 下载模板，确认运行态模板为四 Sheet：
  - `Waybill`
  - `CustomerLine`
  - `OrderLine`
  - `GoodsLine`
- 首次四 Sheet smoke 的真实阻塞：
  - `warehouse_code` 使用了不存在的仓库编码
  - 改为库内真实仓库编码 `WH` 后，`precheck` 转为通过
- 第二个真实阻塞：
  - `CustomerLine` 正式导入报 `maximum recursion depth exceeded`
  - 根因定位在 `logistics.dispatch.waybill.customer.line`

## Fixes

- `logistics_dispatch_waybill_customer_line_v2.py`
  - 去掉 `_compute_partner_fields` 中对 `partner_id` 的反写
  - 将 `store_id` 从可写 related 字段改为只读 related 字段
  - 停止在 `_apply_partner_link` 与 `_normalize_partner_vals` 中回填 `store_id`
- 通过 Odoo shell 点状验证：
  - `logistics.dispatch.waybill.customer.line.create(...)` 已不再递归

## Final Smoke Result

- 真实 smoke 文件：
  - `.smoke/four_sheet_import_smoke_0423182401.xlsx`
- 结果摘要：
  - `.smoke/four_sheet_import_smoke_0423182401.json`
- 任务号：
  - `IMT260423-00010`
- 任务结果：
  - `status = success`
  - `total_count = 12`
  - `success_count = 12`
  - `fail_count = 0`
  - `error_count = 0`

## Database Readback

- 已成功创建：
  - `1` 个波次：`FS-WV-0423182401`
  - `1` 个批次：`FS-BT-0423182401`
  - `2` 个运单：`FS-WB-0423182401-01 / 02`
  - `3` 个 `customer_line`
  - `3` 个 `order_line`
  - `4` 个 `goods_line`
- 客户/门店画像已回写：
  - `res_partner.external_customer_code`
  - `organization_name / department_name / salesperson_name / channel_name`
  - `customer_status / allow_cash_on_delivery / invoice_type`
  - `contact_phone / address_full`
  - `route_preference / warehouse_preference`
  - `receive_start_time / receive_end_time`
  - `delivery_week_flags / delivery_access_flags`
  - `logistics_customer_profile`
  - `logistics_store_profile`

## Boundary

- 本轮 smoke 保留了测试数据与测试任务，便于后续页面回看和人工核验。
- 运行态已验证四 Sheet 主链可真实导入，但历史失败任务与历史 smoke 样本未清理。
