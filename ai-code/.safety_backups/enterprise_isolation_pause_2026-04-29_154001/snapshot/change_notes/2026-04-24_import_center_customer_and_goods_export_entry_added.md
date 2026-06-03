# 2026-04-24 导入中心客户与货物明细导出入口已补齐

## 本次变更

- 在 `custom_addons/logistics_web/static/src/js/actions/import_center_action.js` 将导入中心中的“标准导出”卡片改为按 `source_model` 动态切换，不再只固定显示运单导出入口。
- 为以下导入入口新增对应的导出说明和跳转目标：
  - `logistics.dispatch.waybill` -> 运单列表导出
  - `logistics.dispatch.waybill.customer.line` -> 客户画像列表导出
  - `logistics.dispatch.waybill.customer.goods.line` -> 商品规格列表导出
- 在 `custom_addons/logistics_web/static/src/xml/import_center_templates.xml` 将导出卡片标题、提示文案、按钮文案改为读取 `sourceConfig`，让运单/客户明细/货物明细导入中心显示各自的导出入口。

## 页面行为

- 从“运单导入中心”进入时：
  - 显示“运单标准导出”
  - 按钮跳转 `logistics_dispatch.action_logistics_dispatch_waybill`
- 从“配送节点明细导入”进入时：
  - 显示“客户画像标准导出”
  - 按钮跳转 `logistics_base.action_logistics_partner_profile`
- 从“货物明细导入”进入时：
  - 显示“货物画像标准导出”
  - 按钮跳转 `logistics_base.action_logistics_product_unit`

## 当前状态

- 前端 JS 语法检查已通过：
  - `custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- XML 解析已通过：
  - `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`
- 尚未执行：
  - 浏览器 smoke
  - 页面人工核验

## 下一步建议

- 直接在 3 个导入入口各点一遍：
  - 运单导入中心
  - 配送节点明细导入
  - 货物明细导入
- 确认卡片标题、说明文案和跳转目标都与入口一致。
