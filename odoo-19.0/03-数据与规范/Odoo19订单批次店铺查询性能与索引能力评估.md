# Odoo19订单批次店铺查询性能与索引能力评估

本文档用于回答一个很实际的问题：

如果后面系统正式开发并运行起来，Odoo 自己的数据库对下面这些高频查询支撑能力怎么样：

- 常用订单查询
- 批次查询
- 按店铺查询所有订单
- 按店铺查看相关出库单
- 后续按店铺查运单号、留痕、证据

这里先说明边界：

- 本文结论基于 Odoo 19 源码结构判断
- 不是基于你生产库真实数据量做的 `EXPLAIN ANALYZE`
- 所以这是“结构能力评估”，不是最终压测结论

---

## 1. 先给结论

先直接说判断：

- Odoo 原生对“订单号、出库单号、客户、状态、时间、批次”这类常见 ERP 查询，支持是够用的
- 常见关键字段本身有不少已经带了索引或可搜索能力
- 但是你真正高频的“店铺 -> 订单 -> 运单号 -> 留痕证据”这条新链路，不能只靠 Odoo 原生默认结构
- 如果后面你们业务量上来，必须给自定义运单表、留痕表、证据表单独设计索引

一句话总结：

**Odoo 原生能支撑普通订单和出库查询，但你们真正核心的店铺维度、运单维度、证据维度查询，必须靠自定义表和定制索引来保证性能。**

---

## 2. Odoo 底层数据库类型

这里先提醒一个基础事实：

- Odoo 19 默认数据库是 `PostgreSQL`

所以你后面说“数据库查询性能”，要按 PostgreSQL 的索引和执行计划来理解，不是 MySQL 口径。

Odoo ORM 的常见查询方式是：

- `search(domain, limit, order)`
- `_read_group(...)`
- 关联字段过滤
- 视图搜索栏 filter/group by

只要字段本身有合适索引，这些查询方式都能比较稳定地工作。

---

## 3. 订单查询能力：`sale.order`

从源码看，订单对象 `sale.order` 对这些字段支持比较好：

- `name`：订单号，`trigram` 索引
- `company_id`：公司，显式索引
- `partner_id`：客户，显式索引
- `state`：状态，显式索引
- `create_date`：创建时间，显式索引
- `partner_invoice_id`：开票地址，`btree_not_null`
- `partner_shipping_id`：收货地址，`btree_not_null`
- `user_id`：销售人员，显式索引
- `team_id`：销售团队，显式索引

这意味着下面这些查询，Odoo 原生通常都比较适合：

- 按订单号查订单
- 按客户查订单
- 按收货地址查订单
- 按状态查订单
- 按公司查订单
- 查最近创建订单

对你来说最有用的是：

- `partner_shipping_id` 已经是订单上的正式字段
- 如果你把“店铺”承载为一个 `res.partner` 配送地址或门店主体，那么按店铺查订单是有基础支撑的

但也要注意：

- `date_order` 源码里没有看到显式索引声明
- `warehouse_id` 在 `sale_stock` 扩展里存在，但源码里没有看到显式索引声明

所以如果以后你们特别高频地按“订单日期 + 仓库 + 店铺”联合筛选，原生结构不一定是最优的。

---

## 4. 出库 / 履约查询能力：`stock.picking`

`stock.picking` 是 Odoo 库存执行的核心对象，这张表的可查询能力整体不错。

源码里能明确看到这些重要字段支持搜索或索引：

- `name`：出库单号，`trigram` 索引
- `origin`：来源单号，`trigram` 索引
- `state`：状态，显式索引
- `scheduled_date`：计划时间，显式索引
- `picking_type_id`：操作类型，显式索引
- `partner_id`：联系人，`btree_not_null`
- `company_id`：公司，显式索引
- `batch_id`：批次，显式索引
- `sale_id`：销售订单，`btree_not_null`

所以这些查询原生支撑都比较自然：

- 按出库单号查
- 按来源单号查
- 按状态查
- 按批次查所有出库单
- 按销售订单查相关出库单
- 按客户 / 门店查相关出库单
- 按计划日期查待执行出库单

对于你们的系统，这一层很重要，因为后面很多“订单 / 门店 / 批次”查询都可以先借 `stock.picking` 过渡。

---

## 5. 批次查询能力：`stock.picking.batch`

`stock.picking.batch` 对批次查询有一定支撑，但不是所有字段都天然很强。

源码里能明确看到：

- `company_id`：显式索引
- `state`：显式索引
- `picking_type_id`：显式索引

而这些字段源码里没有看到显式索引声明：

- `name`
- `scheduled_date`
- `warehouse_id`（related）

这意味着：

- 按状态查批次，问题不大
- 按操作类型查批次，问题不大
- 按公司查批次，问题不大
- 但如果你们后面高频按“批次编号”“发货日期”“仓库”联合查，就不建议只依赖默认结构

更直白一点说：

**Odoo 的批次对象更偏流程执行对象，不是为了给你做超高频业务检索而设计的。**

---

## 6. 店铺查询能力：`res.partner`

如果你们把店铺落在 `res.partner` 上，Odoo 也有一定搜索能力。

源码里能明确看到：

- `name`：索引
- `complete_name`：索引
- `ref`：索引
- `parent_id`：索引
- `vat`：索引
- `company_registry`：`btree_not_null`

`res.partner` 的默认搜索名称也支持：

- `complete_name`
- `email`
- `ref`
- `vat`
- `company_registry`

但有个很关键的现实点：

- `zip` 没看到显式索引
- `city` 没看到显式索引

所以如果你们后面经常按：

- 店铺名称
- 店铺编码
- 门店编号

来查，是比较适合的。

但如果大量按：

- 邮编
- 城市
- 地址片区

做高频过滤，就要谨慎，可能需要你们自己补索引或冗余字段。

---

## 7. 你最常用的几类查询，Odoo 原生能不能扛

## 7.1 按店铺查所有订单

可以做，而且基础支撑还不错。

推荐依赖：

- `sale.order.partner_shipping_id`
- 或 `sale.order.partner_id`

如果门店主体在 `res.partner` 里组织清楚，这类查询可以直接走 Odoo ORM domain。

## 7.2 按批次查所有出库单

可以做，而且比较合适。

推荐依赖：

- `stock.picking.batch_id`

这个字段源码里显式带索引，属于 Odoo 比较适合的典型查询。

## 7.3 按订单号查订单 / 出库

可以做。

推荐依赖：

- `sale.order.name`
- `stock.picking.name`
- `stock.picking.origin`

这些字段对搜索支持都不错。

## 7.4 按店铺查所有运单号

这条链 Odoo 原生并没有现成主对象。

也就是说：

- 如果你后面新增 `logistics_dispatch_waybill`
- 那么“按店铺查运单号”性能好不好，主要取决于你自己的表结构和索引，不取决于 Odoo 原生

## 7.5 按店铺看留痕、证据、异常

同理，这已经是你们自定义系统能力了。

Odoo 原生没有替你把：

- 运单号
- 留痕事件
- 证据图片
- 门店签收证明

这条查询链预先建好。

---

## 8. 真正要注意的性能边界

如果只是普通 ERP 查询，Odoo 问题不大。

但你们项目里真正要小心的是下面这些高频链路：

- 按店铺看最近 30 天全部运单
- 按店铺看某天所有交付照片
- 按批次看全部运单及留痕完成情况
- 按司机看当天所有门店交付记录
- 按运单号回看多张图片和异常记录

这些查询的特点是：

- 关联层级多
- 过滤维度多
- 时间范围常常固定在“今天 / 最近 7 天 / 最近 30 天”
- 列表页和详情页都很频繁

这时如果只靠：

- `sale_order`
- `stock_picking`
- `stock_picking_batch`

跨很多层硬查，后面会越来越吃力。

---

## 9. 对你新系统的实际建议

这里我建议分两层看。

## 9.1 可以直接复用 Odoo 的查询基础

这些可以放心复用：

- 按订单号查订单
- 按客户 / 门店查订单
- 按出库单号查出库
- 按批次查出库单
- 按状态查订单 / 出库 / 批次

## 9.2 不要指望 Odoo 原生兜底的部分

这些不要指望 Odoo 默认结构自动帮你扛住：

- 按店铺查所有运单号
- 按运单号查留痕时间线
- 按批次看全部运单完成情况
- 按店铺查看近 30 天多图证据
- 按司机查看门店交付留痕

这些必须靠你们自定义表自己设计。

---

## 10. 自定义表建议补哪些索引

如果你们后面会有：

- 运单表 `logistics_dispatch_waybill`
- 留痕事件表 `logistics_trace_event`
- 证据图片表 `logistics_trace_evidence_image`

那我建议至少优先考虑这些索引方向：

运单表：

- `waybill_no`
- `(store_id, biz_date)`
- `(batch_id, biz_date)`
- `(vehicle_id, biz_date)`
- `(driver_id, biz_date)`
- `(state, biz_date)`

留痕事件表：

- `(waybill_id, trace_type)`
- `(batch_id, trace_type)`
- `(store_id, biz_date)`
- `(state, biz_date)`
- `created_at`

证据图片表：

- `event_id`
- `waybill_id`
- `batch_id`
- `(store_id, biz_date)`
- `(uploaded_at)`

如果再考虑后台高频列表页，还可以继续补：

- `(company_id, biz_date, state)`
- `(store_id, state, biz_date)`
- `(batch_id, state)`

---

## 11. 设计层面的一个关键建议

后面你们不要把所有高频查询都压成“多表现场联查”。

更稳的办法是：

- 主交易表保持规范
- 高频列表页准备轻量查询模型
- 或做面向页面的只读聚合表 / 统计表

例如：

- 店铺运单列表页用 `waybill` 主表直接支撑
- 留痕时间线用 `trace_event` 按运单号直接拉
- 图片清单用 `evidence_image` 按事件或运单直接拉

不要每次都从：

- `sale_order`
- `stock_picking`
- `stock_picking_batch`
- `fleet_vehicle`
- `res_partner`
- `trace_event`
- `evidence_image`

七八张表临时拼出来。

---

## 12. 最终结论

对你的问题，可以直接回答成这样：

- Odoo 原生数据库对常规订单、出库、批次、客户维度查询，是有比较成熟支持的
- 常用关键字段里，订单号、出库单号、客户、状态、批次、计划时间这些维度，本身大多有索引或可搜索能力
- 按店铺查订单，原生也能支撑，前提是店铺主体在 `res.partner` / `partner_shipping_id` 上组织清楚
- 但“店铺 -> 运单号 -> 留痕 -> 证据图片”这条核心链路，Odoo 原生没有直接替你准备好
- 你们自己的运单、留痕、证据表，一定要按真实查询场景单独设计索引

一句话总结：

**Odoo 原生足够做“订单和出库底座查询”，但不够直接做“店铺维度的物流证据检索平台”；真正决定性能上限的，会是你后面自定义运单和留痕表的索引设计。**
