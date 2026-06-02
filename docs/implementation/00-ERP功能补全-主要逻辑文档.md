# ERP 功能补全 — 主要逻辑文档

> 版本: v1.0
> 日期: 2026-06-02
> 目的: 让开发人员理解业务链路全貌和 Odoo 模型设计方案

---

## 一、业务全景

### 1.1 ERP 核心业务链

```
基础档案（供应商/客户/商品/司机/车辆）
    │
    ├── 采购链：采购订单(CG) → 采购入库(RK) → 采购退货(CT) → 采购退货出库(CC)
    │
    ├── 销售链：销售订单(XS) → 销售出库(XC) → 销售退货(XT) → 销售退货入库(RK)
    │
    ├── 结算链：贯穿上述全部单据（已结算/未结算/结算状态）
    │
    └── 报表层：采购4张 + 销售4张 + 看板
```

### 1.2 单据号前缀规律

| 前缀 | 含义 | Odoo 模型 |
|------|------|-----------|
| CG | 采购订单 | `purchase.order` (order_type='standard') |
| RK | 采购入库 / 退货入库 | `stock.picking` (incoming) |
| CT | 采购退货单 | `purchase.order` (order_type='return') |
| CC | 采购退货出库 | `stock.picking` (outgoing, erp_source_type='purchase_return') |
| XS | 销售订单 | `sale.order` |
| XC | 销售出库 | `stock.picking` (outgoing, erp_source_type='sale') + `logistics.dispatch.waybill` |
| XT | 销售退货单 | `erp.sale.return` |
| RK | 销售退货入库 | `stock.picking` (incoming, erp_source_type='sale_return') |

### 1.3 主数据串联关系

| 主数据 | 主键 | 被引用位置 |
|--------|------|-----------|
| 供应商 (`res.partner`, supplier_rank>0) | `ref` / `supplier_rank` | 采购链全部单据 |
| 客户 (`res.partner`, is_logistics_partner=True) | `external_customer_code` | 销售链全部单据 + 报表 |
| 商品 (`product.product`) | `default_code` | 全部业务单据 (12+表) |
| 司机 (`logistics.driver.profile`) | `internal_driver_code` | 销售出库单 |
| 车辆 (`logistics.vehicle.profile`) | `internal_vehicle_code` | 物流运单 |

---

## 二、设计方案总览

### 2.1 设计原则

1. **类型区分优先于新建模型** — 采购退货复用 `purchase.order` 加 `order_type`
2. **Mixin 解决跨模型通用字段** — 结算三字段通过 Abstract Model 一次定义
3. **只在没有承载模型时才新建** — 仅 `erp.sale.return.line` 必须新建
4. **复用 Odoo 原生能力** — 预付款用 `account.payment`，补货用 `stock.warehouse.orderpoint`

### 2.2 改动分类

| 类型 | 数量 | 包含 |
|------|------|------|
| 新建模型 | 2 | `erp.sale.return.line`, `erp.settlement.mixin` |
| 扩展现有模型 | 6 | purchase.order, stock.picking, stock.move, sale.order, erp.sale.return, stock.warehouse.orderpoint |
| 字段追加 | 3 | res.partner 供应商字段 |

---

## 三、模型设计详细方案

### 3.1 采购退货单 — 复用 `purchase.order`

**核心思路**：采购退货单和采购订单字段重叠 90%，只需加 `order_type` 字段区分。

**新增字段（`purchase.order` 扩展）：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `order_type` | Selection | `standard`=标准采购, `return`=采购退货 |
| `return_reason` | Text | 退货原因 |
| `source_picking_id` | Many2one → stock.picking | 原入库单 |
| `source_order_id` | Many2one → purchase.order | 原采购订单 |
| `department_id` | Many2one → hr.department | 部门 |

**业务逻辑：**
- 退货单确认后，自动生成 `stock.picking`（outgoing）并设置 `erp_source_type = 'purchase_return'`
- 退货金额为正数（Odoo 内部用正数 + 方向标记处理）
- 视图上通过 `domain=[('order_type', '=', 'return')]` 筛选出退货单列表

**与 ERP 表的字段映射：**

| ERP 字段 | Odoo 字段 | 说明 |
|----------|-----------|------|
| 单据号 | `name` | 自动编号，CT 前缀 |
| 单据日期 | `date_order` | 原生字段 |
| 供应商 | `partner_id` | 原生字段 |
| 采购员 | `user_id` | 原生字段 |
| 仓库 | `warehouse_id` | 已有扩展字段 |
| 部门 | `department_id` | 新增 |
| 退货原因 | `return_reason` | 新增 |
| 商品明细 | `order_line` (purchase.order.line) | 原生 |
| 审核状态 | `state` | 原生 |
| 结算字段 | Mixin 继承 | 见 3.4 |

---

### 3.2 采购退货出库 — 复用 `stock.picking`

**核心思路**：已有 `erp_source_type = 'purchase_return'` 选项，零改动。

**流转逻辑：**
1. 采购退货单（`purchase.order`, order_type='return'）确认
2. 系统自动创建 `stock.picking`：
   - `picking_type_code = 'outgoing'`
   - `erp_source_type = 'purchase_return'`
   - `origin = 退货单.name`（关联源单）
3. 仓库执行出库操作

**视图筛选**：`domain=[('erp_source_type', '=', 'purchase_return'), ('picking_type_code', '=', 'outgoing')]`

---

### 3.3 销售退货入库 — 复用 `stock.picking`

**核心思路**：退货商品进入仓库 = incoming + sale_return 类型。

**新增字段（`stock.picking` 扩展）：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `sale_return_id` | Many2one → erp.sale.return | 关联销售退货单 |
| `recovery_status` | Selection | 回收状态（待回收/已回收/不适用） |

**流转逻辑：**
1. 销售退货单（`erp.sale.return`）确认
2. 创建入库 `stock.picking`：
   - `picking_type_code = 'incoming'`
   - `erp_source_type = 'sale_return'`
   - `sale_return_id = 退货单.id`

**与 ERP 4.8 退货入库单详情的映射：**

| ERP 字段 | Odoo 字段 |
|----------|-----------|
| 入库单号 | `stock.picking.name` |
| 退货单号 | `sale_return_id.name` |
| 门店编号/名称 | `partner_id` |
| 仓库 | `picking_type_id.warehouse_id` |
| 商品明细 | `stock.move` + `stock.move.line` |
| 实际数量 | `stock.move.quantity_done` |
| 回收状态 | `recovery_status` |
| 结算字段 | Mixin 继承 |

---

### 3.4 结算体系 — Mixin 模式

**核心思路**：8 张单据都需要 `已结算金额/未结算金额/结算状态`，用 Abstract Model 一次定义。

**Mixin 定义：**

```python
class ErpSettlementMixin(models.AbstractModel):
    _name = "erp.settlement.mixin"
    _description = "结算字段 Mixin"

    amount_settled = fields.Monetary(string="已结算金额", default=0, currency_field='currency_id')
    amount_unsettled = fields.Monetary(string="未结算金额", compute='_compute_unsettled', store=True)
    settlement_state = fields.Selection([
        ('unsettled', '未结算'),
        ('partial', '部分结算'),
        ('settled', '已结算'),
    ], default='unsettled', string="结算状态", compute='_compute_settlement_state', store=True)
```

**继承模型列表：**

| 模型 | `amount_total` 来源 |
|------|-------------------|
| `purchase.order` | 原生 `amount_total` |
| `sale.order` | 原生 `amount_total` |
| `stock.picking` | 需新增计算字段（汇总 move 的 sale_price_subtotal） |
| `erp.sale.return` | 已有 `amount_total` |

**业务规则：**
- `amount_unsettled = amount_total - amount_settled`
- 当 `amount_settled == 0` → `unsettled`
- 当 `0 < amount_settled < amount_total` → `partial`
- 当 `amount_settled >= amount_total` → `settled`
- 结算动作通过 `erp.reconciliation`（已有对账模型）触发更新

---

### 3.5 销售退货明细行 — 新建 `erp.sale.return.line`

**模型定义：**

| 字段名 | 类型 | 说明 | ERP 对应 |
|--------|------|------|----------|
| `return_id` | Many2one → erp.sale.return | 退货主表 | — |
| `product_id` | Many2one → product.product | 商品 | 商品编号 |
| `product_uom` | Many2one → uom.uom | 单位 | 基本单位/单据单位 |
| `qty` | Float | 退货数量 | 单据数量 |
| `qty_base` | Float | 基本单位数量 | 基本单位数量 |
| `price_unit` | Float | 退货单价 | 单据退货单价 |
| `price_subtotal` | Float (compute) | 退货金额 | 退货金额 |
| `return_reason` | Char | 行级退货原因 | 退货原因 |
| `note` | Text | 明细备注 | 明细备注 |

**同时补全 `erp.sale.return` 主表：**

| 新增字段 | 类型 | 说明 |
|----------|------|------|
| `line_ids` | One2many → erp.sale.return.line | 明细行 |
| `user_id` | Many2one → res.users | 业务员 |
| `department_id` | Many2one → hr.department | 部门 |
| `warehouse_id` | Many2one → stock.warehouse | 仓库 |
| `source_shipment_no` | Char | 源单单号（出库单 XC） |
| `delivery_method` | Selection | 配送方式 |

---

### 3.6 预付/预收体系

**采购预付（`purchase.order` 扩展）：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `advance_payment_ids` | Many2many → account.payment | 关联预付款单 |
| `advance_payment_state` | Selection (compute) | 无预付/待审核/已审核 |
| `advance_payment_amount` | Monetary (compute) | 累计预付金额 |
| `advance_payment_number` | Char (compute) | 付款单号汇总 |

**销售预收（`sale.order` 扩展）：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `advance_receipt_ids` | Many2many → account.payment | 关联预收款单 |
| `advance_receipt_state` | Selection (compute) | 无预收/待审核/已审核 |
| `advance_receipt_amount` | Monetary (compute) | 累计预收金额 |

---

### 3.7 出库单明细价格 — 扩展 `stock.move`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `sale_price_unit` | Float | 销售单价（从 sale.order.line 同步） |
| `sale_price_subtotal` | Float (compute) | 销售金额 = sale_price_unit × quantity |

**同步时机**：`stock.picking` 确认出库时，从关联的 `sale.order.line.price_unit` 写入。

---

### 3.8 智能补货 — 扩展 `stock.warehouse.orderpoint`

| 字段名 | 类型 | 说明 | ERP 对应 |
|--------|------|------|----------|
| `fixed_purchase_qty` | Float | 固定采购量 | 固定采购量 |
| `replenishment_strategy` | Selection | 补货策略 | 补货策略 |
| `forecast_method` | Char | 预测方案 | 预测方案 |
| `in_transit_qty` | Float (compute) | 在途数量 | 在途数量 |
| `on_hand_qty` | Float (compute) | 在库数量 | 在库数量 |

Odoo 原生已有：`product_min_qty`(安全库存), `product_max_qty`(目标库存), `product_id`, `warehouse_id`

---

### 3.9 供应商字段补全 — 扩展 `res.partner`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `arrival_days` | Integer | 到货天数 |
| `supplier_external_code` | Char | 供应商金蝶外部编码 |
| `purchase_price_type` | Selection | 采购价格类型（净价/含税价/合同价） |

---

## 四、模型关系总图

```
purchase.order (order_type: standard|return)
    ├── purchase.order.line (商品明细)
    ├── ← erp.settlement.mixin (结算字段)
    ├── → stock.picking (确认后生成入库/出库)
    └── → account.payment (预付款关联)

sale.order
    ├── sale.order.line (商品明细)
    ├── ← erp.settlement.mixin (结算字段)
    ├── → stock.picking (出库)
    ├── → logistics.dispatch.waybill (物流运单)
    └── → account.payment (预收款关联)

stock.picking (erp_source_type: sale|purchase|sale_return|purchase_return)
    ├── stock.move (商品明细行 + sale_price_unit)
    ├── stock.move.line (批次/序列号)
    ├── ← erp.settlement.mixin (结算字段)
    └── → wms.outbound.task / wms.receipt.task (WMS任务)

erp.sale.return
    ├── erp.sale.return.line (商品明细 - 新建)
    ├── ← erp.settlement.mixin (结算字段)
    └── → stock.picking (退货入库)

stock.warehouse.orderpoint (智能补货)
    └── → purchase.order (自动生成采购建议)
```

---

## 五、前端表格视图要求

客户要求所有业务单据以**表格形式**展示，Odoo 中对应：

| 视图类型 | 说明 | 用于 |
|----------|------|------|
| List View (tree) | 单据列表页 | 所有列表页（采购订单列表、退货单列表等） |
| Form View | 单据详情页 | 带主表+明细行的表单 |
| One2many inline tree | 明细行编辑 | 订单行/退货行/出库行 |
| Search View | 筛选/分组 | 按类型(order_type)、状态、日期筛选 |
| Pivot/Graph View | 报表汇总 | 采购/销售报表 |

关键筛选域示例：
- 采购订单列表：`[('order_type', '=', 'standard')]`
- 采购退货单列表：`[('order_type', '=', 'return')]`
- 销售出库单列表：`[('erp_source_type', '=', 'sale'), ('picking_type_code', '=', 'outgoing')]`
- 销售退货入库列表：`[('erp_source_type', '=', 'sale_return'), ('picking_type_code', '=', 'incoming')]`

---

## 六、参考文档

| 文档 | 路径 | 说明 |
|------|------|------|
| ERP 字段对比分析 | `ai-code/docs/context/gap_analysis/field_comparison.md` | 两遍对比完整结果 |
| ERP 模板原始字段 | `docs/erp_template/` | 30 张 Excel 提取 |
| 实施路线图 | `docs/implementation/implementation_roadmap.md` | 优先级排列 |
| Odoo 全量模型清单 | `ai-code/docs/context/gap_analysis/odoo_models_full.md` | 102 模型 |
