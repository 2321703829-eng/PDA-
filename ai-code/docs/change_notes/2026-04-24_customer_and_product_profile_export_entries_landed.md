# 2026-04-24 客户画像与货物画像导出入口已落地

## 本次变更

- 在 `custom_addons/logistics_web/static/src/js/components/list_import_button.js` 扩展列表页导出按钮分发：
  - `res.partner` 物流客户画像列表可直接发起 `customer_profile`
  - `product.template` 商品列表可直接发起 `product_profile`
  - `logistics.product.unit` 商品规格列表可直接发起 `product_profile`
- 商品规格列表发起导出时，会先读取 `product_tmpl_id`，按商品主档去重后再调用正式导出接口。
- 在 `custom_addons/logistics_web/models/res_partner.py` 新增客户画像表单导出入口：
  - `action_open_customer_profile_export_result`
- 在 `custom_addons/logistics_web/models/product_template.py` 新增商品主档表单导出入口：
  - `action_open_product_profile_export_result`
- 在 `custom_addons/logistics_web/models/logistics_product_unit.py` 新增商品规格表单导出入口：
  - `action_open_product_profile_export_result`
- 在 `custom_addons/logistics_web/views/logistics_web_profile_views.xml` 为以下表单补了“导出结果”按钮：
  - 物流客户画像表单
  - 商品规格表单
  - 商品主档表单

## 结果页补充

- 在 `custom_addons/logistics_web/static/src/js/actions/export_result_action.js` 补充 `product_profile` 的来源页回跳：
  - 如果来源页是 `product_unit_list / product_unit_form`，结果页返回商品规格列表
  - 其他 `product_profile` 入口仍返回商品列表

## 当前状态

- Python AST 检查已通过：
  - `custom_addons/logistics_web/models/res_partner.py`
  - `custom_addons/logistics_web/models/product_template.py`
  - `custom_addons/logistics_web/models/logistics_product_unit.py`
  - `custom_addons/logistics_web/models/__init__.py`
  - `custom_addons/logistics_web/__manifest__.py`
- 前端 JS 语法检查已通过：
  - `custom_addons/logistics_web/static/src/js/components/list_import_button.js`
  - `custom_addons/logistics_web/static/src/js/actions/export_result_action.js`
- XML 解析已通过：
  - `custom_addons/logistics_web/views/logistics_web_profile_views.xml`
- 尚未执行：
  - Odoo 模块升级
  - 浏览器 smoke
  - 客户画像与货物画像导出联调

## 下一步建议

- 直接升级 `logistics_web` 模块并做浏览器 smoke。
- 手工走 4 条链路：
  - 客户画像列表导出
  - 客户画像表单导出
  - 商品规格列表导出
  - 商品规格表单导出
