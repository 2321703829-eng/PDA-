# 2026-04-24 客户画像与货物画像导出正式落库与接口冻结补丁稿新增

## This round

- 在现有标准批量导出正式冻结稿之上，新增客户画像与货物画像导出的正式落库与接口补丁稿。
- 将前一轮专题方案进一步推进到可直接进入开发拆分的冻结层。

## Added files

- [客户画像与货物画像导出正式落库与接口冻结补丁稿](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-24_客户画像与货物画像导出正式落库与接口冻结补丁稿.md>)

## Key decisions

- 正式新增两类导出对象：
  - `customer_profile`
  - `product_profile`
- 正式新增货物画像入口类型：
  - `from_product`
- 正式新增包结构：
  - `customer_profile_bundle_v1 / v2`
  - `product_profile_bundle_v1 / v2`
- 正式新增通用统计字段方向：
  - `export_task.package_metrics_json`
  - `export_task_line.line_metrics_json`
- 正式新增创建路由：
  - `POST /api/admin/logistics/exports/customer-profile`
  - `POST /api/admin/logistics/exports/product-profile`
- 正式明确：
  - 客户画像导出主对象是 `res.partner`
  - 货物画像导出主对象是 `product.template`
  - 不新增独立 `goods_profile` 表

## Next

- 继续补 `from_customer / from_product` 首轮开发任务拆分单
- 再进入模型、service、controller、结果页与入口按钮的分包实现
