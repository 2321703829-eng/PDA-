# 2026-04-24 客户画像与货物画像导出方案新增

## This round

- 新增客户画像与货物画像导出的专题方案，作为 `from_waybill` 之后的下一组正式业务导出设计基线。
- 明确这两条导出线不再长期依赖 Odoo 原生字段导出，而是复用当前已落地的正式任务结果链。

## Added files

- [客户画像与货物画像导出模块设计方案](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-24_客户画像与货物画像导出模块设计方案.md>)

## Key decisions

- 客户画像导出主对象统一收口到 `res.partner`，不再以 `logistics.customer.profile` / `logistics.store.profile` 作为正式导出主源。
- 货物画像导出主对象统一收口到 `product.template`，并由 `logistics.product.unit` 承接规格层，不新增一张独立 `goods_profile` 表。
- 客户画像导出首轮建议文件结构：
  - `CustomerProfile`
- 货物画像导出首轮建议文件结构：
  - `ProductProfile`
  - `ProductUnit`
- 当 `logistics.customer.product.profile` 后续落地后，再同时增强客户画像和货物画像导出中的 `CustomerProductRelation` 表达。
- 当前 `export_task` / `export_task_line` 的统计字段属于 `dispatch_main` 专用口径，后续正式冻结时应新增：
  - `package_metrics_json`
  - `line_metrics_json`
  以支持客户画像和货物画像导出复用同一结果页模型。

## Next

- 补“客户画像与货物画像导出正式落库与接口冻结补丁稿”
- 补 `from_customer / from_product` 首轮开发任务拆分单
