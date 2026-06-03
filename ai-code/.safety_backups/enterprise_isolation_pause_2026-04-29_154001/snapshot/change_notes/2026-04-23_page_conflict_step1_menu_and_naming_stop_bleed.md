# 2026-04-23 页面去打架第一步：菜单与命名止血

## 本次改动

按页面去打架清单正式执行第一步：

- 收掉原生应用根菜单挂入物流根的逻辑
- 恢复原生应用入口可见
- 将 `客户明细` 系列命名统一改为 `配送节点明细`

## 涉及文件

- `custom_addons/logistics_web/models/ui_label_sync.py`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`

## 具体调整

### 1. 原生菜单恢复为顶层

在 `ui_label_sync.py` 中不再把下面这些菜单挂到物流根下：

- `contacts.menu_contacts`
- `hr.menu_hr_root`
- `fleet.menu_root`
- `stock.menu_stock_root`
- `account.menu_finance`
- `base.menu_administration`

并在同步时显式恢复：

- `parent_id = False`
- `active = True`

### 2. 运单客户节点改名

把运单执行链路里的 `客户明细` 改成：

- `配送节点明细`

把相关导入入口改成：

- `配送节点明细导入`

同步调整了：

- 运单详情 smart button
- 运单详情页签
- 列表、表单、搜索视图标题
- act_window / client action 名称
- 调度菜单名称

## 数据库升级

执行：

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init
```

## 升级后核验结果

已确认：

- `contacts.menu_contacts` 为 `active = True`
- `hr.menu_hr_root` 为顶层菜单
- `fleet.menu_root` 为顶层菜单
- `stock.menu_stock_root` 为顶层菜单
- `account.menu_finance` 为顶层菜单
- `base.menu_administration` 为顶层菜单
- `logistics_dispatch.menu_logistics_dispatch_waybill_customer_line` 名称为 `配送节点明细`
- `logistics_dispatch.action_logistics_dispatch_waybill_customer_line` 名称为 `配送节点明细`
- `logistics_dispatch.action_logistics_dispatch_waybill_customer_line_import_center_direct` 名称为 `配送节点明细导入`

## 结果

第一步已经完成，物流根下的入口结构明显收口，后续可以继续做第二步：

- 司机管理 / 车辆管理页收口为“运营驾驶舱 + 跳转”
