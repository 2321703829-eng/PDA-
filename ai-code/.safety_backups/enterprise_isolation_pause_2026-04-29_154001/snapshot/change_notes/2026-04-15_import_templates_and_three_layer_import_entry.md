# 2026-04-15 导入模板入口与运单三层导入路径落地

## Objective

继续落地 `2026-04-15_天枢科技物流后台品牌化重构与首页及订单导入重设计方案.md` 中与导入中心、标准模板、运单/客户/货物三层导入有关的实现。

## 本轮改动

1. 给 `logistics.dispatch.waybill`、`logistics.dispatch.waybill.customer.line`、`logistics.dispatch.waybill.customer.goods.line` 补了标准模板入口。
2. 在 `logistics_dispatch` 模块静态资源下新增 3 份可下载模板：
   - `logistics_dispatch_waybill_import_template.csv`
   - `logistics_dispatch_waybill_customer_line_import_template.csv`
   - `logistics_dispatch_waybill_customer_goods_line_import_template.csv`
3. 在 `物流 -> 导入中心` 下新增 3 条分层导入路径：
   - `运单导入`
   - `客户明细导入`
   - `货物明细导入`
4. 新增两个 `ir.actions.client(tag=import)`：
   - `action_logistics_dispatch_waybill_customer_line_import_center_direct`
   - `action_logistics_dispatch_waybill_customer_goods_line_import_center_direct`
5. 新增客户明细与货物明细的 v2 模型文件，避免继续受旧编码残留文件影响：
   - `logistics_dispatch_waybill_customer_line_v2.py`
   - `logistics_dispatch_waybill_customer_goods_line_v2.py`
6. 货物明细导入支持按 `waybill_no + customer_no` 或 `waybill_no + customer_name` 反解 `customer_line_id`，从而允许独立导入货物层数据。
7. `ui_label_sync.py` 同步补上了新的导入中心子菜单结构，避免升级后菜单被写回旧结构。

## 影响范围

- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- `custom_addons/logistics_dispatch/models/__init__.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_line_v2.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_goods_line_v2.py`
- `custom_addons/logistics_web/models/ui_label_sync.py`
- `custom_addons/logistics_dispatch/static/src/import_templates/`

## Verify

已完成：

- Python 源码级 `compile(...)` 校验通过：
  - `logistics_dispatch_waybill.py`
  - `logistics_dispatch_waybill_customer_line_v2.py`
  - `logistics_dispatch_waybill_customer_goods_line_v2.py`
  - `__init__.py`
  - `ui_label_sync.py`
- XML 结构解析通过：
  - `logistics_dispatch_waybill_views.xml`
  - `logistics_dispatch_menus.xml`
- 模板文件已创建并可枚举。

未完成：

- Odoo 模块升级后的实际页面验收
- 三条导入入口在浏览器中的人工点击验证
- `customer_line_id` 反解链路的真实导入验收

## Next

升级 `logistics_dispatch, logistics_web` 后，优先核验：

1. `物流 -> 导入中心` 下是否出现 `运单导入 / 客户明细导入 / 货物明细导入`
2. 三个导入页是否都出现对应模板下载按钮
3. 货物模板上传后，`waybill_no + customer_no` 是否能正确命中客户明细
