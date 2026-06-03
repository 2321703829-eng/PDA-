# `logistics_customer_product_profile` 字段清单 + 唯一约束方案

## Status

- 当前状态：后续规划
- 本期结论：本期先不落库、不建模、不改导入主链
- 使用方式：作为下一阶段商品主数据深化方案的预研设计

## Objective

在“全局商品主档 + 客户商品关系层 + 运单货物执行层”的三层方案下，补齐第二层正式数据库设计：

- 用一张独立关系表表达“某客户如何使用某商品”
- 不重复录入商品本体长期属性
- 不把客户侧默认单位、签收要求、包装要求继续塞进运单执行层
- 给后续导入、主数据维护、页面入口提供统一结构

## Outcome

本方案落地后，数据库层应形成以下边界：

- `product.template` 负责商品本体长期主数据
- `logistics_product_unit` 负责商品规格 / SKU / 销售单位层
- `logistics_customer_product_profile` 负责客户与商品之间的关系规则
- `goods_line` 继续负责“这次送了什么”的执行事实与必要快照

补充说明：

- 上述 Outcome 属于后续目标态，不是本期必须完成状态。

## Boundary

本文只覆盖：

- `logistics_customer_product_profile` 的字段设计
- 唯一约束方案
- 建议索引
- 与 `logistics_product_unit`、`goods_line` 的边界

本文不直接覆盖：

- 前端页面交互细节
- 导入模板逐列映射
- 运单执行表的重构细节
- 客户/门店单对象收口的页面命名问题

## Benchmark

当前系统里已经存在的基础层：

- 商品主档：`product.template`
- 商品规格层：`logistics.product.unit`
- 运单货物执行层：`logistics.dispatch.waybill.goods.line`

当前缺口不是“商品主档不存在”，而是缺少一层显式关系来表达：

- 某客户常用哪些商品
- 某客户对某商品默认使用哪个销售单位
- 某客户对某商品是否有专属编码、签收要求、包装要求、温层要求

## Recommended Model

- 模型名：`logistics.customer.product.profile`
- 表名：`logistics_customer_product_profile`

## Recommended Grain

首轮推荐粒度直接定为：

- 一条记录 = 一个客户 + 一个商品 + 一个销售单位关系

这样做的原因：

- 能直接承接客户默认订货单位
- 能避免“客户只挂商品本体，但默认用哪个单位仍然不清楚”
- 唯一约束可以直接稳定落成三键

## Recommended Fields

### 1. 主关系键

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `partner_id` | `Many2one('res.partner')` | 是 | 客户对象 |
| `product_tmpl_id` | `Many2one('product.template')` | 是 | 商品本体 |
| `product_unit_id` | `Many2one('logistics.product.unit')` | 是 | 客户默认使用的销售单位 |

### 2. 客户侧识别字段

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `customer_product_code` | `Char(64)` | 否 | 客户侧商品编码 |
| `customer_product_name_alias` | `Char(128)` | 否 | 客户侧商品别名 |

### 3. 客户侧默认规则字段

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `default_signoff_requirement` | `Text` | 否 | 该客户对该商品的默认签收要求 |
| `default_package_requirement_text` | `Text` | 否 | 客户侧包装要求 |
| `default_temperature_zone` | `Char(32)` | 否 | 温层要求，如常温/冷藏/冷冻 |
| `allow_substitute_unit` | `Boolean` | 否 | 是否允许替代销售单位 |
| `min_delivery_qty` | `Float` | 否 | 客户侧最小配送数量 |
| `is_frequently_ordered` | `Boolean` | 否 | 是否常用商品 |
| `is_disabled` | `Boolean` | 否 | 是否对该客户停用 |
| `sort_order` | `Integer` | 否 | 客户商品清单展示顺序 |
| `relation_remark` | `Text` | 否 | 客户商品关系备注 |

### 4. 审计与通用字段

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `company_id` | `Many2one('res.company')` | 否 | 公司维度 |
| `active` | `Boolean` | 否 | 软停用 |

## Recommended Unique Constraint

首轮正式推荐方案：

```text
unique(partner_id, product_tmpl_id, product_unit_id)
```

含义是：

- 同一个客户
- 对同一个商品
- 在同一个销售单位粒度下
- 只允许存在一条有效关系记录

这是当前最稳的做法，因为它避免了下面两类歧义：

- 一个客户对同一商品既有“产品级关系”又有“单位级关系”
- `product_unit_id` 可空时，很难清晰表达默认单位到底是哪一个

## Recommended Data Integrity Rules

除唯一约束外，建议再补两条数据完整性规则：

1. `product_unit_id.product_tmpl_id` 必须等于 `product_tmpl_id`
2. `is_disabled = True` 时，不删除历史关系，仅停用

第一条可以用 Python 约束或数据库检查逻辑实现；首轮不要求写复杂 SQL Check，也至少要在模型层挡住脏数据。

## Recommended Indexes

建议至少补这些索引：

```text
idx_lcpp_partner_id(partner_id)
idx_lcpp_product_tmpl_id(product_tmpl_id)
idx_lcpp_product_unit_id(product_unit_id)
idx_lcpp_partner_active_freq(partner_id, active, is_frequently_ordered)
```

如后续客户商品清单频繁按客户编码搜索，可再加：

```text
idx_lcpp_partner_customer_product_code(partner_id, customer_product_code)
```

## Fields That Should Not Be Repeated Here

以下字段不建议再复制到 `logistics_customer_product_profile`：

- 商品品牌
- 商品分类
- 商品全局条码
- 商品标准重量 / 体积
- 商品规格尺寸
- 商品标准价 / 采购价 / 零售价

这些仍应以：

- `product.template`
- `logistics_product_unit`

为主事实来源。

## Relationship With Execution Layer

`goods_line` 仍应保留：

- `product_tmpl_id`
- `product_unit_id`
- 必要商品快照

但它不应继续承担客户商品长期关系职责。

后续更推荐的命中顺序是：

1. 先命中 `partner_id`
2. 再命中 `product_tmpl_id`
3. 再命中 `product_unit_id`
4. 如命中 `logistics_customer_product_profile`，优先带出客户默认规则

## DTO / Import Impact Summary

新增该表后，接口与导入层至少会增加一类对象：

- 客户商品关系 DTO

推荐最小请求体：

```json
{
  "partner_id": 2001,
  "product_tmpl_id": 1001,
  "product_unit_id": 3001,
  "customer_product_code": "KH-A-0001",
  "customer_product_name_alias": "矿泉水标准箱",
  "default_signoff_requirement": "需门店负责人签收",
  "default_package_requirement_text": "整箱配送，不拆零",
  "default_temperature_zone": "常温",
  "allow_substitute_unit": false,
  "min_delivery_qty": 1.0,
  "is_frequently_ordered": true,
  "is_disabled": false,
  "sort_order": 10,
  "relation_remark": ""
}
```

## Phase Recommendation

首轮推荐按下面顺序实施：

1. 先新增 `logistics_customer_product_profile`
2. 先打通客户商品关系的主数据维护
3. 运单执行层先兼容读取，不强制重构
4. 本期先保留为设计预案，待商品主数据和导入口径稳定后再正式开发
4. 后续再逐步把导入和执行层收口到“主档优先 + 关系层优先”
