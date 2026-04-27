# 全局商品主档 + 客户商品关系层 + 运单货物执行层 三层收口方案

## Objective

建立一套更稳定的货品建模边界：

- 同一个货品只在系统里维护一份长期主数据
- 多个客户/门店复用同一商品主档，不再重复录入商品本体信息
- 客户侧只维护“客户和商品之间的关系信息”
- 运单层只记录本次实际送了什么，不承担长期商品主数据职责

## Boundary

本方案只讨论商品相关三层收口：

- 全局商品主档
- 客户商品关系层
- 运单货物执行层

本方案不覆盖：

- 司机/车辆画像
- 客户/门店主对象收口
- 导入页面交互改造
- 排线与调度状态层

## Benchmark

当前项目里已经存在的基础：

- 商品主档：`product.template`
  - [product_template.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/product_template.py:1)
- 商品规格 / SKU 层：`logistics.product.unit`
  - [logistics_product_unit.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/logistics_product_unit.py:1)
- 运单货物执行层：`logistics.dispatch.waybill.customer.goods.line`
  - [logistics_dispatch_waybill_customer_goods_line_v2.py](/D:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_goods_line_v2.py:1)

当前数据库设计稿里的主张也已经偏向这个方向：

- 商品主档优先复用 `product.template`
- 商品规格层使用 `logistics_product_unit`
- 运单层保留商品快照，不强依赖主档一直不变
  - [四期数据库底表设计稿](/D:/Desktop/Odoo/ai-code/专题设计/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期数据库底表设计稿%20v1（第二次修正版）.md:103)

## Current Understanding

### 当前已经做对的部分

1. 商品本体已经有全局主档基础。
   - `product.template` 承接商品编码、名称、品牌、分类、默认重量、默认体积等长期属性

2. 商品规格层已经单独拆出来。
   - `logistics.product.unit` 承接 SKU / 规格 / 销售单位 / 条码 / 价格 / 尺寸 / 单位换算

3. 运单货物执行层已经和主档发生关联。
   - `goods_line` 上有 `product_tmpl_id`
   - `goods_line` 上有 `product_unit_id`

### 当前还不够稳定的部分

1. 客户和商品之间没有独立的“关系层”。
   - 现在不是“商品主档没了”，而是“客户如何使用这个商品”还没独立建模

2. 执行层和导入层仍然偏重快照。
   - `goods_line` 上保留了大量商品名称、规格、条码、品牌等快照字段
   - 这对保历史是必要的，但也容易让团队误以为商品信息应该在执行层维护

3. 目前缺少“同一商品被多客户共享”的显式业务结构。
   - 也就是缺少一张客户商品关系表来表达：
     - 某客户常用哪些商品
     - 某客户对该商品有没有专属编码或特殊规则

## 三层方案

## 第一层：全局商品主档

### 角色

系统级唯一商品本体，不按客户重复维护。

### 推荐承载模型

- `product.template`
- `logistics.product.unit`

### 应保留在这一层的字段

#### 商品本体层：`product.template`

- 内部商品编码
- 外部商品编码
- 商品名称
- 品牌
- 分类
- 商品标签
- 默认条码
- 基础单位
- 默认重量
- 默认体积
- 商品通用配送要求

#### 商品规格 / SKU 层：`logistics.product.unit`

- 所属商品
- SKU 编号
- 规格描述
- 销售单位
- 换算系数
- 条码
- 标准价
- 采购价
- 零售价
- 长宽高
- 重量
- 体积

### 这一层的规则

1. 一个商品本体只录一份。
2. 一个商品可对应多个规格 / 销售单位。
3. 这一层不记录“某客户专属”的规则。
4. 这一层不记录“某次运单实际送了多少”。

## 第二层：客户商品关系层

### 角色

表达“某客户如何使用这个商品”，而不是重复录商品本体。

### 建议新增模型

- 暂定：`logistics.customer.product.profile`

更准确地说，这不是“商品画像”，而是“客户商品关系表”。

### 建议主键关系

- `partner_id -> res.partner`
- `product_tmpl_id -> product.template`
- `product_unit_id -> logistics.product.unit` 可空

建议唯一约束：

- `unique(partner_id, product_tmpl_id, product_unit_id)`

如果业务上客户维度只精确到商品本体，也可以先用：

- `unique(partner_id, product_tmpl_id)`

### 应该放在这一层的字段

- 客户专属商品编码
- 客户常用商品标记
- 客户是否禁售
- 客户默认下单单位
- 客户默认签收要求
- 客户对该商品的包装要求
- 客户对该商品的温层要求
- 客户是否允许替代规格
- 客户最小配送量
- 客户侧备注

### 不应该放在这一层的字段

- 商品品牌
- 商品名称
- 商品分类
- 商品标准条码
- 商品标准尺寸
- 商品标准价格

这些都属于全局商品主档，不应按客户重复录。

## 第三层：运单货物执行层

### 角色

表达“这一次到底送了什么、送了多少、按什么规格送、金额是多少”。

### 当前承载模型

- `logistics.dispatch.waybill.customer.goods.line`

### 应保留在这一层的字段

- `customer_line_id`
- `order_line_id`
- `waybill_id`
- `product_tmpl_id`
- `product_unit_id`
- 数量
- 件数
- 金额
- 温层
- 包装类型
- 本次执行备注

### 应保留的快照字段

为了保证历史运单可追溯，这些快照仍然需要保留：

- 商品编码快照
- 商品名称快照
- 规格快照
- 条码快照
- 品牌快照
- 类别快照
- 标签快照
- 单位快照

### 这一层的规则

1. 执行层优先关联商品主档和规格层。
2. 执行层允许保留快照，但快照不是主维护来源。
3. 执行层如果没有命中主档，也可先保留快照落单，后续再补命中。

## 关系图

```text
res.partner
   └─ logistics.customer.product.profile
        ├─ product.template
        └─ logistics.product.unit

product.template
   └─ logistics.product.unit

logistics.dispatch.waybill
   └─ logistics.dispatch.waybill.customer.line
        └─ logistics.dispatch.waybill.customer.goods.line
             ├─ product.template
             └─ logistics.product.unit
```

## 页面口径建议

### 1. 客户页面

客户页面不要再出现“客户自己有一套商品主档”的表达。

更合适的入口应该是：

- `客户常用商品`
- `客户商品关系`

### 2. 商品页面

商品页面应是全局入口，谁都复用。

更合适的结构：

- 商品主档
- 商品规格
- 被哪些客户常用

### 3. 运单货物页

运单货物页应该强调：

- 这是本次执行货物
- 引用商品主档
- 保留快照

不应该让用户误解为“在这里维护商品长期信息”。

## 导入口径建议

导入层也应该跟着三层走：

### 全局商品导入

维护：

- 商品本体
- 商品规格 / 单位

### 客户商品关系导入

维护：

- 某客户和某商品之间的专属规则

### 运单执行导入

维护：

- 本次运单里实际送了哪些商品

## 开发顺序建议

### 第一阶段

先不动现有 `goods_line` 主结构，只补一层客户商品关系模型。

目标：

- 先解决“同一商品被多客户复用”问题
- 不影响现有运单导入和执行链

### 第二阶段

逐步把导入和页面的“商品长期信息”从执行层迁回主档层。

目标：

- 执行层只留必要快照
- 商品长期信息真正单点维护

### 第三阶段

再评估是否需要独立“商品画像”表。

我的建议是：

- 如果只是商品主数据 + 客户商品关系，**不需要新增 `goods_profile`**
- 只有当物流专属长期属性明显超出 `product.template + logistics.product.unit + customer_product_relation` 时，才再建第四层

## Final Recommendation

对你刚刚提的业务诉求，最准确的落地不是“再建一张货物画像表”，而是：

1. 商品本体统一进 `product.template`
2. 商品规格统一进 `logistics.product.unit`
3. 新增一张 `客户商品关系表`
4. 运单货物明细只做执行事实 + 快照

这样才能真正实现：

- 一个货品被多家客户共享
- 商品长期信息只维护一次
- 客户差异化规则单独表达
- 运单历史仍然可追溯

