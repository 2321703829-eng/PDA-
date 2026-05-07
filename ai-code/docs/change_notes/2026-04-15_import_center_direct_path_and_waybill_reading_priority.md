# 2026-04-15 导入中心直达导入路径与运单详情主次阅读优化

## 本次处理

- 将 `物流 -> 导入中心` 从普通运单列表入口改为直接打开 Odoo 标准导入页。
- 新增 `ir.actions.client` 版本的导入中心动作，直接承接 `tag = import`。
- 运单详情页中将 `订单明细` 明确降级为 `原始订单明细（兼容）`。
- 运单详情顶部统计按钮顺序调整为：
  - 客户明细
  - 货物明细
  - 原始订单明细
- 在原始订单明细页签中增加说明文案，引导用户优先查看客户明细和货物明细。

## 影响文件

- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`

## 目的

- 让导入中心真正承担“标准导入路径”的角色，而不是落回普通列表页。
- 让运单详情中的客户/货物结构成为主阅读路径，原始订单明细只保留为兼容核对区。
