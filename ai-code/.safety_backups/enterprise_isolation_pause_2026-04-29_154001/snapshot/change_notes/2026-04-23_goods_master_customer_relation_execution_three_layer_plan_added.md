# 2026-04-23 全局商品主档 + 客户商品关系层 + 运单货物执行层 三层方案补充

## 背景

业务进一步确认：

- 同一个货品可能被多家客户/门店需要
- 商品本体信息不应在每个客户侧重复录入
- 真正需要区分的，不是“每个客户有自己的商品主档”，而是“每个客户和商品之间的关系规则”

## 本次输出

新增方案文档：

- `ai-code/docs/dev/goods_master_customer_relation_execution_three_layer_plan.md`

## 核心结论

商品相关结构推荐收口为三层：

1. 全局商品主档
   - `product.template`
   - `logistics.product.unit`

2. 客户商品关系层
   - 建议新增 `logistics.customer.product.profile`
   - 用于表达客户专属商品编码、常用标记、默认单位、包装/温层/签收要求等

3. 运单货物执行层
   - `logistics.dispatch.waybill.customer.goods.line`
   - 只表达本次送了什么、送了多少，并保留必要快照

## 目的

避免继续把“商品长期主数据”混在客户侧或运单执行层里维护，真正实现：

- 商品全局复用
- 客户差异规则单独表达
- 运单历史仍可追溯
