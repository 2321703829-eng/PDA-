# 2026-04-24 导出结果页客户画像与货物画像分支已落地

## 本次变更

- 在 `custom_addons/logistics_web/static/src/js/actions/export_result_action.js` 将导出结果页改为按 `object_type` 分支渲染，不再只按 `dispatch_main` 的运单导出视角展示。
- 为 `customer_profile` 新增结果页摘要卡片：
  - 总任务行
  - 成功
  - 失败
  - 跳过
  - 导出客户
- 为 `product_profile` 新增结果页摘要卡片：
  - 总任务行
  - 成功
  - 失败
  - 跳过
  - 导出商品
  - 导出规格
- 保留 `dispatch_main` 原有摘要卡片：
  - 导出运单
  - 导出节点
  - 导出订单
  - 导出货物
- 将结果页顶部提示文案和返回动作改为按对象类型适配：
  - `dispatch_main` 返回运单列表
  - `customer_profile` 返回客户画像列表
  - `product_profile` 返回商品列表

## 返回入口

- 客户画像结果页返回：
  - `logistics_base.action_logistics_partner_profile`
- 货物画像结果页返回：
  - `stock.product_template_action_product`

## 当前状态

- 前端 JS 语法检查已通过：
  - `custom_addons/logistics_web/static/src/js/actions/export_result_action.js`
- 导出结果页模板 XML 解析已通过：
  - `custom_addons/logistics_web/static/src/xml/export_result_templates.xml`
- 尚未执行：
  - 浏览器 smoke
  - 真实 `customer_profile / product_profile` 导出联调

## 下一步建议

- 继续做 `CP-EXP-F2` 和 `PP-EXP-F2`，把客户画像页与货物画像页的入口按钮接上。
- 入口按钮接好后，直接做浏览器 smoke，分别走一遍客户画像导出和货物画像导出。
