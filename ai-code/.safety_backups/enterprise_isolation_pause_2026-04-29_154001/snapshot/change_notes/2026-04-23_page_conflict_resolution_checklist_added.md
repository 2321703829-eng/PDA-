# 2026-04-23 页面去打架改造清单补充

## 本次补充

新增页面去打架改造清单文档：

- `docs/dev/page_conflict_resolution_checklist.md`

## 文档目的

把当前物流系统中客户 / 门店 / 司机 / 车辆与 Odoo 原生页面之间的冲突问题，整理成一份可执行的改造 runbook。

## 清单覆盖内容

- 菜单入口收口
- 运营页定位收口
- 画像菜单权限收口
- 数据所有权收口

## 关键落点

- `custom_addons/logistics_web/models/ui_label_sync.py`
- `custom_addons/logistics_web/views/logistics_web_menus.xml`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`
- `custom_addons/logistics_base/views/logistics_base_profile_views.xml`
- `custom_addons/logistics_base/views/res_partner_views.xml`
- `custom_addons/logistics_base/views/hr_employee_views.xml`
- `custom_addons/logistics_base/views/fleet_vehicle_views.xml`

## 结果

后续可以按该清单分步骤执行实际改造，不需要再先做一次高层归纳。

## 后续补充

同日补充了回滚记录建议，加入：

- 回滚锚点记录方式
- 当前数据库基线
- 执行登记模板

这样后续正式改菜单、动作和入口时，可以直接按文档登记并支持回滚。
