# 2026-04-23 `logistics_customer_product_profile` 设计清单与四期设计稿同步

## 本次变更

- 新增 [logistics_customer_product_profile_schema_checklist.md](/D:/Desktop/Odoo/ai-code/docs/dev/logistics_customer_product_profile_schema_checklist.md:1)，明确客户商品关系层的字段清单、唯一约束方案、索引建议与边界。
- 更新 [2026-04-21_四期数据库底表设计稿 v1（第二次修正版）.md](/D:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期数据库底表设计稿%20v1（第二次修正版）.md:1)，同步商品主数据四层收口口径，并补充 `logistics_customer_product_profile` 字段与约束摘要。
- 更新 [2026-04-21_四期后端数据库与接口影响面调研稿.md](/D:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期后端数据库与接口影响面调研稿.md:1)，同步数据库影响面和客户商品关系 DTO 口径。
- 新增 [2026-04-23_客户商品关系层数据库与接口补充设计.md](/D:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-23_客户商品关系层数据库与接口补充设计.md:1)，作为四期商品主数据收口的专项补充稿。

## 影响范围

- 仅文档与设计口径更新
- 本次未改数据库代码、未改 Odoo 模型、未执行模块升级

## 当前结论

- 商品主数据继续坚持方案 B：`logistics_product_unit` 一条记录只表达一个销售单位。
- 客户侧商品差异化规则不再回塞到 `logistics_product_unit` 或执行层，后续推荐新增 `logistics_customer_product_profile` 承接。
- 但该对象当前只保留在设计中，已明确标注为后续规划，不纳入本期正式落地范围。
