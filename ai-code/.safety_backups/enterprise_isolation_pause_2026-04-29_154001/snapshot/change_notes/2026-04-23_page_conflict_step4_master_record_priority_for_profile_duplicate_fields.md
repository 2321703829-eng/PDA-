# 2026-04-23 页面去打架第四步：画像重复字段收口回主档

## 变更目标

按 `docs/dev/page_conflict_resolution_checklist.md` 的第四步执行，把客户/门店/司机画像中与主档重复的字段收口回主档，改成“主档优先，画像只读展示”。

## Outcome

- 客户画像中的基础身份字段不再作为画像独立编辑源
- 门店画像中的名称、地址、经纬度不再作为画像独立编辑源
- 司机画像中的编号、姓名、联系电话不再作为画像独立编辑源
- 主档创建画像时不再写入这些重复字段

## Behavior

### 客户画像

以下字段改为 `related + store + readonly`：

- `customer_level -> partner_id.logistics_customer_level`
- `customer_status -> partner_id.customer_status`
- `registered_phone -> partner_id.contact_phone`
- `registered_address -> partner_id.address_full`
- `customer_seq_no -> partner_id.logistics_customer_code`

### 门店画像

以下字段改为 `related + store + readonly`：

- `address_code -> partner_id.logistics_store_code`
- `external_customer_code -> partner_id.external_customer_code`
- `customer_name -> partner_id.customer_name`
- `address_full -> partner_id.address_full`
- `longitude -> partner_id.partner_longitude`
- `latitude -> partner_id.partner_latitude`

### 司机画像

以下字段改为主档驱动：

- `internal_driver_code -> employee_id.logistics_employee_code`
- `driver_name -> employee_id.name`
- `driver_phone -> 由 employee.mobile_phone / work_phone / private_phone 计算`

### 车辆画像

本轮未新增字段收口。当前车辆画像页里没有与 `fleet.vehicle` 直接重复、且作为主编辑入口暴露的字段，因此先保持现状。

## Boundary

- 本轮不删除画像表中的物流专属字段
- 本轮不改变车辆画像中的物流专属字段
- 本轮不新增复杂迁移脚本，仅补充现有开发库存量字段回刷

## 变更文件

- `custom_addons/logistics_base/models/logistics_customer_profile.py`
- `custom_addons/logistics_base/models/logistics_store_profile.py`
- `custom_addons/logistics_base/models/logistics_driver_profile.py`
- `custom_addons/logistics_base/models/res_partner.py`
- `custom_addons/logistics_base/models/hr_employee.py`
- `custom_addons/logistics_base/migrations/19.0.1.1.0/post-migration.py`
- `docs/dev/page_conflict_resolution_checklist.md`

## 实现说明

### 主档创建画像

以前主档上的“打开或创建画像”动作会把冗余字段一起写入画像表。

本轮已收掉这些重复写入：

- `res.partner` 创建客户/门店画像时，不再写基础身份字段
- `hr.employee` 创建司机画像时，不再写司机姓名、司机电话

### 存量数据回刷

由于开发库里已经有少量存量画像记录，本轮对 `odoo_logistics_phase4_v1` 执行了一次主档字段回刷，确保当前测试库立即和新口径一致。

同时也把同样的同步逻辑补进了：

- `custom_addons/logistics_base/migrations/19.0.1.1.0/post-migration.py`

用于后续已有库升级时参考和复用。

## 升级与验证

执行命令：

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_base --stop-after-init
```

额外执行：

- 对当前开发库补做一次主档字段同步

验证结果：

- 模型文件通过 Python 语法校验
- 相关 XML 通过解析校验
- `logistics_base` 模块升级成功
- 抽样核对当前测试数据：
  - 门店画像名称、地址与 `res.partner` 一致
  - 司机画像姓名、联系电话与 `hr.employee` 一致
  - 客户画像编号、地址与 `res.partner` 一致

## 风险提示

- `customer_seq_no` 现在明确收口到 `res.partner.logistics_customer_code`，如果后续团队仍想保留独立“客户序号”概念，需要单独重新建模
- 这一步解决的是“字段所有权”，不是“画像字段精简”的全部工作
