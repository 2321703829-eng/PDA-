# 2026-04-27 `logistics_base` 主数据写入与同步链修复

## 本次变更

修复了 `logistics_base + logistics_dispatch` 主数据写入与同步链的 3 个问题：

1. 主数据编码唯一性缺口
2. `waybill.partner_id` 递归写死
3. snapshot 自动回填缺失

## 代码修改

### `custom_addons/logistics_base/models/res_partner.py`

- 补充唯一约束：
  - `logistics_customer_code`
  - `logistics_store_code`
  - `internal_customer_code`
- 编码归一化时统一 `strip()`
- 空字符串归一为 `False`
- `logistics_customer_code` / `logistics_store_code` 强制保持统一口径

### `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py`

- `partner_id` 改成普通存储字段，不再用 computed+inverse 写回
- 新增 `_prepare_partner_link_vals()`
- 统一在 `_normalize_partner_vals()` 里收口 `partner/customer/store`
- 解析客户编码时补入 `logistics_store_code`
- 新增 `waybill` snapshot 自动回填

### `custom_addons/logistics_dispatch/models/logistics_dispatch_wave.py`

- 新增 `wave` snapshot helper
- create/write 时自动回填：
  - `organization_name_snapshot`
  - `warehouse_name_snapshot`

### `custom_addons/logistics_dispatch/models/logistics_dispatch_batch.py`

- 新增 `batch` snapshot helper
- create/write 时自动回填：
  - `warehouse_name_snapshot`
  - `route_name_snapshot`
  - `driver_name_snapshot`
  - `driver_phone_snapshot`

### `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_line_v2.py`

- 解析客户编码时补入 `logistics_store_code`
- 新增客户节点 snapshot helper
- create/write 时自动回填联系人、电话、地址、签收要求等快照

### `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_order_line.py`

- 新增订单行 snapshot helper
- create/write 时自动回填部门、渠道、业务员快照

## 验证

- AST 语法解析通过
- `logistics_base, logistics_dispatch` 升级通过
- `logistics_dispatch` 二次升级通过
- shell smoke 通过：
  - 重复编码被 `UniqueViolation` 拦下
  - `partner_id` 直建 `waybill` 成功
  - `wave/batch/waybill/customer_line/order_line` 关键 snapshot 已自动落值

## 报告

- 修复报告：
  - `docs/review/findings/2026-04-27_base_master_sync_fix_report.md`
