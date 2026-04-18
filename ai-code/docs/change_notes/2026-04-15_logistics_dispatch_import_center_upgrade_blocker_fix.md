# 2026-04-15 导入中心直达动作升级阻断修复
## 问题现象

- `logistics_dispatch` 模块升级后，`物流 -> 导入中心` 仍然落到旧的运单列表动作。
- 数据库中一度查不到 `logistics_dispatch.action_logistics_dispatch_waybill_import_center_direct` 的 XMLID。

## 根因

- 阻断点不在新建的 `ir.actions.client` 本身，而在同一文件
  `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`
  更前面的运单表单视图。
- 该视图在“原始订单明细（兼容） -> 使用说明”区域使用了不符合 Odoo 19 视图校验规则的
  `<label .../>`，升级时触发：
  `Label tag must contain a "for"...`
- 因为整份 `logistics_dispatch_waybill_views.xml` 会在该错误处回滚，所以文件尾部新增的
  `action_logistics_dispatch_waybill_import_center_direct`
  也不会入库。

## 修复

- 将说明区域的 `label` 改为带 `o_form_label` 样式的普通元素：
  - 由 `<label .../>`
  - 改为 `<div><span class="o_form_label">...</span></div>`
- 重新升级 `logistics_dispatch` 和 `logistics_web` 后确认：
  - `action_logistics_dispatch_waybill_import_center_direct` 已入库
  - 其 `tag = import`
  - `menu_logistics_dispatch_import_center` 已绑定到 `ir.actions.client,523`

## 影响文件

- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`

