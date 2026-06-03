# 2026-04-27 logistics_web profile 查询口径与权限收口修复

## 本次变更

- 修复 `driver / vehicle` 页面仍按 `waybill.store_id` 统计门店的问题，改为优先读取 `waybill.customer_line_ids.partner_id`，兼容一个运单多个配送节点。
- 新增 `logistics.driver.profile.driver_remark` 字段，并将 `driver profile` 概览接口的 `remark` 改为读取该正式字段，不再引用当前模型中不存在的 `hr.employee.notes/note`。
- 将 `group_logistics_analysis_viewer` 收口为显式继承 `group_logistics_driver_management_viewer`，保证统计中心跳转到司机管理页时权限链一致。

## 影响文件

- `custom_addons/logistics_web/models/logistics_driver_service.py`
- `custom_addons/logistics_web/models/logistics_vehicle_service.py`
- `custom_addons/logistics_base/models/logistics_driver_profile.py`
- `custom_addons/logistics_base/views/logistics_base_profile_views.xml`
- `custom_addons/logistics_web/security/logistics_web_security.xml`

## 验证

- Python 语法检查通过：`logistics_driver_service.py`、`logistics_vehicle_service.py`、`logistics_driver_profile.py`
- XML 解析检查通过：`logistics_base_profile_views.xml`、`logistics_web_security.xml`、`logistics_web_actions.xml`
- 模块升级通过：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_base,logistics_web --stop-after-init`
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_web --stop-after-init`
- 最小 shell smoke 通过：
  - 临时双配送节点运单在 driver recent waybills 中展示为合并门店名
  - 临时双配送节点运单在 vehicle recent waybills 中展示为合并门店名
  - `driver_overview.remark` 正常返回临时写入的 `driver_remark`
  - `analysis viewer` 临时用户可直接访问 `getDriverList`

## 说明

- 验证过程中曾尝试给 `ir.actions.client` 增加 `groups_id`，升级时确认 Odoo 19 当前实现不支持该字段；最终采用“分析查看组继承司机管理查看组”的方式完成权限收口。
