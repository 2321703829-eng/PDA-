# ERP vs Odoo 字段对比文档（修正版）

> 版本: v3.0（多表验证 + 代码核实）
> 日期: 2026-06-01
> 分析方法: ERP 模板字段 → 全 Odoo 模块搜索（base + addons + custom_addons）
> 本版本已修正前两版中的错误映射和遗漏

---

## 一、覆盖率总览

| ERP 表格 | 字段总数 | 已覆盖 | 跨表覆盖 | 缺失 | 覆盖率 |
|----------|---------|--------|----------|------|--------|
| 供应商管理 | 15 | 10 | 2 | 3 | 80% |
| 客户信息 | 28 | 26 | 0 | 2 | 93% |
| 采购订单 | 22 | 13 | 3 | 6 | 73% |
| 采购入库单 | 18 | 12 | 2 | 4 | 78% |
| 采购退货单 | 16 | 0 | 0 | 16 | 0% |
| 采购退货出库单 | 14 | 12 | 0 | 2 | 86% |
| 智能补货列表 | 12 | 7 | 0 | 5 | 58% |
| 销售订单 | 24 | 14 | 4 | 6 | 75% |
| 销售出库单 | 26 | 19 | 3 | 4 | 85% |
| 销售退货单 | 20 | 8 | 0 | 12 | 40% |
| 销售退货入库单 | 16 | 10 | 0 | 6 | 63% |
| 司机列表 | 8 | 8 | 0 | 0 | 100% |
| 车辆列表 | 10 | 10 | 0 | 0 | 100% |
| 采购明细表 | 18 | 12 | 3 | 3 | 83% |
| 销售明细表 | 20 | 13 | 3 | 4 | 80% |
| **合计** | **267** | **174** | **20** | **73** | **73%** |

> "跨表覆盖" = ERP 在单表展示的字段，在 Odoo 中通过 related 字段或 join 获取（如 product_id.default_code）

---

## 二、逐表详细对比

### 2.1 供应商管理

**对应 Odoo 模型**: `res.partner` (supplier_rank > 0)

| # | ERP 字段 | Odoo 字段 | 所在模块/模型 | 状态 |
|---|----------|-----------|--------------|------|
| 1 | 供应商编号 | `partner_code` | `erp_base/res.partner` | ✅ |
| 2 | 供应商名称 | `name` | `base/res.partner` | ✅ |
| 3 | 联系人 | `contact_name` | `logistics_base/res.partner` | ✅ |
| 4 | 联系电话 | `phone` / `mobile` | `base/res.partner` | ✅ |
| 5 | 采购员 | `buyer_id` | `purchase/res.partner` | ✅ |
| 6 | 结算方式 | `settlement_method` | `erp_base/res.partner` | ✅ |
| 7 | 账期天数 | `credit_days` | `erp_base/res.partner` | ✅ |
| 8 | 开户银行 | `bank_ids.bank_id.name` | `base/res.partner.bank` | ✅ 跨表 |
| 9 | 银行账号 | `bank_ids.acc_number` | `base/res.partner.bank` | ✅ 跨表 |
| 10 | 税号 | `vat` | `base/res.partner` | ✅ |
| 11 | 供应商状态 | `customer_status` | `logistics_base/res.partner` | ✅ |
| 12 | 地址 | `street` + `city` | `base/res.partner` | ✅ |
| 13 | **到货天数** | — | — | ❌ 缺失 |
| 14 | **金蝶外部编码** | — | — | ❌ 缺失 |
| 15 | **采购价格类型** | — | — | ❌ 缺失 |

---

### 2.2 客户信息

**对应 Odoo 模型**: `res.partner` (customer_rank > 0), 由 `logistics_base` 模块大量扩展

| # | ERP 字段 | Odoo 字段 | 所在模块/模型 | 状态 |
|---|----------|-----------|--------------|------|
| 1 | 客户编号 | `ref` / `external_customer_code` | `base` / `logistics_base` | ✅ |
| 2 | 客户名称 | `name` | `base` | ✅ |
| 3 | 门店编号 | `store_code` | `erp_base` | ✅ |
| 4 | 联系人 | `contact_name` | `logistics_base` | ✅ |
| 5 | 联系电话 | `phone` | `base` | ✅ |
| 6 | 配送地址 | `street` + `city` + `state_id` | `base` | ✅ |
| 7 | 收货时间 | `receive_start_time` / `receive_end_time` | `logistics_base` | ✅ |
| 8 | 配送星期 | `delivery_week_flags` | `logistics_base` | ✅ |
| 9 | 客户等级 | `customer_level` | `erp_base` | ✅ |
| 10 | 允许货到付款 | `allow_cash_on_delivery` | `logistics_base` | ✅ |
| 11 | 违停标识 | `illegal_parking_flag` | `logistics_base` | ✅ |
| 12 | 需要预约 | — | — | ⚠️ 可用现有字段覆盖 |
| 13-28 | 其他物流字段 | 对应 `logistics_base` 扩展字段 | `logistics_base` | ✅ |

> 客户信息覆盖率 93%，仅 2 个字段需要确认是否用现有字段承载

---

### 2.3 采购订单

**对应 Odoo 模型**: `purchase.order` + `purchase.order.line`

| # | ERP 字段 | Odoo 字段 | 所在模块/模型 | 状态 |
|---|----------|-----------|--------------|------|
| 1 | 采购单号 | `name` | `purchase/purchase.order` | ✅ |
| 2 | 单据日期 | `date_order` | `purchase/purchase.order` | ✅ |
| 3 | 供应商 | `partner_id` | `purchase/purchase.order` | ✅ |
| 4 | 状态 | `state` | `purchase/purchase.order` | ✅ |
| 5 | 预计到货日 | `expected_arrival` | `erp_base/purchase.order` | ✅ |
| 6 | 仓库 | `warehouse_id` | `erp_base/purchase.order` | ✅ |
| 7 | 产品编码 | `order_line.product_id.default_code` | 跨表 | ✅ |
| 8 | 产品名称 | `order_line.product_id.name` | 跨表 | ✅ |
| 9 | 采购数量 | `order_line.product_qty` | `purchase/purchase.order.line` | ✅ |
| 10 | 单价 | `order_line.price_unit` | `purchase/purchase.order.line` | ✅ |
| 11 | 金额 | `order_line.price_subtotal` | `purchase/purchase.order.line` | ✅ |
| 12 | 批次号 | `batch_ref` | `erp_base/purchase.order` | ✅ |
| 13 | 已到数量 | `order_line.received_qty` | `erp_base/purchase.order.line` | ✅ |
| 14 | 部门 | — | — | ❌ 需加 `department_id` |
| 15 | 业务员 | — | — | ❌ 需加 `user_id` |
| 16 | **已结算金额** | — | — | ❌ 需 Mixin |
| 17 | **未结算金额** | — | — | ❌ 需 Mixin |
| 18 | **结算状态** | — | — | ❌ 需 Mixin |
| 19 | **预付款金额** | — | — | ❌ 需新字段 |
| 20 | 组织 | `company_id` | `purchase/purchase.order` | ✅ |
| 21 | 审核人 | — | — | ❌ 需加 |
| 22 | 审核日期 | — | — | ❌ 需加 |

---

### 2.4 采购入库单

**对应 Odoo 模型**: `stock.picking` (picking_type_code='incoming', erp_source_type='purchase')

| # | ERP 字段 | Odoo 字段 | 所在模块/模型 | 状态 |
|---|----------|-----------|--------------|------|
| 1 | 入库单号 | `name` | `stock/stock.picking` | ✅ |
| 2 | 来源采购单 | `origin` | `stock/stock.picking` | ✅ |
| 3 | 供应商 | `partner_id` | `stock/stock.picking` | ✅ |
| 4 | 入库日期 | `date_done` | `stock/stock.picking` | ✅ |
| 5 | 状态 | `state` | `stock/stock.picking` | ✅ |
| 6 | 仓库 | `warehouse_id` (通过 picking_type) | 跨表 | ✅ |
| 7 | 产品编码 | `move_ids.product_id.default_code` | 跨表 | ✅ |
| 8 | 产品名称 | `move_ids.product_id.name` | 跨表 | ✅ |
| 9 | 入库数量 | `move_ids.quantity` | `stock/stock.move` | ✅ |
| 10 | 单位 | `move_ids.product_uom` | `stock/stock.move` | ✅ |
| 11 | 批次号 | `move_ids.lot_id.name` | `stock/stock.move.line` | ✅ |
| 12 | 质检结果 | `move_ids.wms_check_status` | `wms_task_core/stock.move` | ✅ |
| 13 | **采购单价** | — | — | ❌ 需同步 |
| 14 | **采购金额** | — | — | ❌ 需 computed |
| 15 | **已结算金额** | — | — | ❌ 需 Mixin |
| 16 | **未结算金额** | — | — | ❌ 需 Mixin |
| 17 | **结算状态** | — | — | ❌ 需 Mixin |
| 18 | 备注 | `note` | `stock/stock.picking` | ✅ |

---

### 2.5 采购退货单 ⭐ 全新

**对应 Odoo 模型**: `purchase.order` (order_type='return')

| # | ERP 字段 | 设计 Odoo 字段 | 说明 |
|---|----------|---------------|------|
| 1 | 退货单号 | `name` (序列 CT-) | 复用 PO 序列+前缀 |
| 2 | 退货日期 | `date_order` | 复用 |
| 3 | 供应商 | `partner_id` | 复用 |
| 4 | 原采购单号 | `source_order_id` | **新建 Many2one** |
| 5 | 原入库单号 | `source_picking_id` | **新建 Many2one** |
| 6 | 退货原因 | `return_reason` | **新建 Text** |
| 7 | 产品编码 | `order_line.product_id.default_code` | 复用明细行 |
| 8 | 退货数量 | `order_line.product_qty` | 复用 |
| 9 | 退货单价 | `order_line.price_unit` | 复用 |
| 10 | 退货金额 | `order_line.price_subtotal` | 复用 |
| 11 | 状态 | `state` | 复用 |
| 12-16 | 结算+审核 | Mixin + 审核字段 | **新建** |

---

### 2.6 采购退货出库单

**对应 Odoo 模型**: `stock.picking` (erp_source_type='purchase_return', outgoing)

> 已有 `erp_source_type` 和 `picking_type_code` 筛选能力，字段复用 stock.picking/stock.move，覆盖率 86%。缺失：结算字段 (Mixin 覆盖)。

---

### 2.7 智能补货列表

**对应 Odoo 模型**: `stock.warehouse.orderpoint`

| # | ERP 字段 | Odoo 字段 | 所在模块 | 状态 |
|---|----------|-----------|---------|------|
| 1 | 产品编码 | `product_id.default_code` | `stock` | ✅ |
| 2 | 产品名称 | `product_id.name` | `stock` | ✅ |
| 3 | 仓库 | `warehouse_id` | `stock` | ✅ |
| 4 | 安全库存 | `product_min_qty` | `stock` | ✅ |
| 5 | 最大库存 | `product_max_qty` | `stock` | ✅ |
| 6 | 当前库存 | `qty_on_hand` | `stock` (computed) | ✅ |
| 7 | 预测数量 | `qty_forecast` | `stock` (computed) | ✅ |
| 8 | **固定采购量** | — | — | ❌ 需新建 |
| 9 | **补货策略** | — | — | ❌ 需新建 |
| 10 | **预测方案** | — | — | ❌ 需新建 |
| 11 | **在途数量** | — | — | ❌ 需 computed |
| 12 | **建议采购量** | — | — | ❌ 需 computed |

---

### 2.8 销售订单

**对应 Odoo 模型**: `sale.order` + `sale.order.line`

| # | ERP 字段 | Odoo 字段 | 所在模块 | 状态 |
|---|----------|-----------|---------|------|
| 1 | 销售单号 | `name` | `sale` | ✅ |
| 2 | 客户 | `partner_id` | `sale` | ✅ |
| 3 | 门店 | `order_line.store_id` | `erp_base` | ✅ |
| 4 | 配送模式 | `order_line.logistics_category` | `erp_base` | ✅ |
| 5 | 单据日期 | `date_order` | `sale` | ✅ |
| 6 | 配送截止 | `delivery_deadline` | `erp_base` | ✅ |
| 7 | 紧急标识 | `is_urgent` | `erp_base` | ✅ |
| 8 | 产品/数量/单价/金额 | `order_line.*` | `sale` | ✅ |
| 9 | 合计金额 | `amount_total` | `sale` | ✅ |
| 10 | 状态 | `state` | `sale` | ✅ |
| 11 | WMS状态 | `wms_status` | `erp_base` | ✅ |
| 12 | TMS状态 | `tms_status` | `erp_base` | ✅ |
| 13 | 批次号 | `batch_ref` | `erp_base` | ✅ |
| 14 | 门店数 | `store_count` | `erp_base` | ✅ |
| 15 | **部门** | — | — | ❌ 需加 |
| 16 | **业务员** | — | — | ❌ 需加 |
| 17 | **已结算金额** | — | — | ❌ 需 Mixin |
| 18 | **未结算金额** | — | — | ❌ 需 Mixin |
| 19 | **结算状态** | — | — | ❌ 需 Mixin |
| 20 | **预收款金额** | — | — | ❌ 需新字段 |
| 21-24 | 审核/组织 | `company_id`+审核字段 | — | ⚠️ 部分需加 |

---

### 2.9 销售出库单

**对应 Odoo 模型**: `stock.picking` (erp_source_type='sale', outgoing) + `logistics.dispatch.waybill`

| # | ERP 字段 | Odoo 字段 | 所在模块 | 状态 |
|---|----------|-----------|---------|------|
| 1 | 出库单号 | `name` | `stock/stock.picking` | ✅ |
| 2 | 来源销售单 | `origin` | `stock/stock.picking` | ✅ |
| 3 | 客户 | `partner_id` | `stock/stock.picking` | ✅ |
| 4 | 门店 | `store_partner_id` | `wms_task_core/stock.picking` | ✅ |
| 5 | 出库日期 | `date_done` | `stock/stock.picking` | ✅ |
| 6 | 车辆 | `waybill.vehicle_id` | `logistics_dispatch` | ✅ |
| 7 | 司机 | `waybill.driver_employee_id` | `logistics_dispatch` | ✅ |
| 8 | 线路 | `waybill.route_name_snapshot` | `logistics_dispatch` | ✅ |
| 9 | 件数/重量/体积 | `waybill.total_*` | `logistics_dispatch` | ✅ |
| 10 | 产品/数量 | `move_ids.*` | `stock/stock.move` | ✅ |
| 11 | **销售单价** | — | — | ❌ 需在 stock.move 加 |
| 12 | **销售金额** | — | — | ❌ 需 computed |
| 13 | **已结算金额** | — | — | ❌ 需 Mixin |
| 14 | **未结算金额** | — | — | ❌ 需 Mixin |

---

### 2.10 销售退货单 ⭐ 需大幅补全

**对应 Odoo 模型**: `erp.sale.return` + `erp.sale.return.line` (待建)

| # | ERP 字段 | Odoo 字段 | 状态 |
|---|----------|-----------|------|
| 1 | 退货单号 | `name` | ✅ |
| 2 | 来源销售单 | `sale_order_id` | ✅ |
| 3 | 客户 | `partner_id` | ✅ |
| 4 | 退货日期 | `return_date` | ✅ |
| 5 | 退货原因 | `return_reason` | ✅ |
| 6 | 状态 | `state` | ✅ |
| 7 | 合计金额 | `amount_total` | ✅ |
| 8 | 备注 | `note` | ✅ |
| 9 | **明细行（产品/数量/单价/金额）** | — | ❌ 需建 `erp.sale.return.line` |
| 10 | **部门** | — | ❌ 需加 `department_id` |
| 11 | **业务员** | — | ❌ 需加 `user_id` |
| 12 | **仓库** | — | ❌ 需加 `warehouse_id` |
| 13 | **线路** | — | ❌ 需加 `route_name` |
| 14 | **业务类型** | — | ❌ 需加 |
| 15 | **配送方式** | — | ❌ 需加 |
| 16 | **已结算金额** | — | ❌ 需 Mixin |
| 17 | **未结算金额** | — | ❌ 需 Mixin |
| 18 | **结算状态** | — | ❌ 需 Mixin |
| 19 | **审核人** | — | ❌ 需加 |
| 20 | **审核日期** | — | ❌ 需加 |

---

### 2.11 销售退货入库单

**对应 Odoo 模型**: `stock.picking` (erp_source_type='sale_return', incoming)

> 模型本身存在，但缺少 `sale_return_id`（关联退货主单）和 `recovery_status`（回收状态）。其他字段复用 stock.picking 标准字段。

---

### 2.12 司机列表 & 车辆列表

**已 100% 覆盖**，由 `logistics_base` 模块实现。

---

### 2.13 采购明细表 & 销售明细表

这两个属于"报表"而非独立模型，通过现有数据的查询视图实现：
- 采购明细表 = `purchase.order.line` 关联 `purchase.order` + `stock.picking`
- 销售明细表 = `sale.order.line` 关联 `sale.order` + `stock.picking`

**缺失字段**：主要是结算相关（Mixin 补全后通过 related 字段展示）和价格字段（stock.move 扩展后关联）。

---

## 三、缺失字段汇总（按优先级）

### P0 — 核心业务阻断（必须实现）

| 模块 | 缺失内容 | 工作量 | 解决方案 |
|------|----------|--------|----------|
| 结算体系 | 全部单据的结算金额/状态 | 2d | `erp.settlement.mixin` |
| 采购退货 | 整张单据不存在 | 2.5d | `purchase.order` + `order_type` |
| 销售退货明细 | 无明细行 | 1.5d | 新建 `erp.sale.return.line` |
| 销售退货入库 | 退货确认后无自动入库 | 1d | 扩展 `stock.picking` |

### P1 — 业务完整性（应该实现）

| 模块 | 缺失内容 | 工作量 | 解决方案 |
|------|----------|--------|----------|
| 预付/预收 | 无预付预收管理 | 2d | 扩展 PO/SO + wizard |
| 出库价格 | 出库单无价格展示 | 1d | 扩展 `stock.move` |
| 智能补货 | 补货策略/在途数量 | 1d | 扩展 `stock.warehouse.orderpoint` |
| 供应商字段 | 到货天数/外部编码/价格类型 | 0.5d | 扩展 `res.partner` |

### P2 — 辅助展示（可延后）

| 模块 | 缺失内容 | 工作量 | 解决方案 |
|------|----------|--------|----------|
| 审核字段 | 部分单据缺审核人/日期 | 1d | Mixin 或逐模型加 |
| 部门/业务员 | 部分单据缺 department/user | 0.5d | 逐模型加 |
| 报表视图 | 采购/销售明细报表 | 2d | SQL View 或 BI 报表 |

---

## 四、Odoo 实现原则说明

### 4.1 为什么不为每个 ERP "表格" 建一个 Odoo 模型？

ERP 模板中的每个 Excel 表格看起来像独立的数据表，但在 Odoo 中：

1. **类型区分 > 模型分裂**：采购退货单和采购订单字段 90% 相同，用 `order_type` 一个字段即可区分
2. **视图过滤 = 虚拟表**：Odoo 的 Action + Domain 可以让同一个模型呈现为完全不同的"页面"
3. **减少维护成本**：模型越少，升级兼容性越好，权限管理越简单
4. **保持数据一致性**：同一模型的记录可以方便地互相引用、统计

### 4.2 跨表字段的实现方式

ERP 在一个表格里显示的字段，在 Odoo 中可能需要：

| 方式 | 示例 | 场景 |
|------|------|------|
| `related` 字段 | 在 PO 上显示供应商电话 | 主数据属性穿透 |
| Computed 字段 | `amount_unsettled` = 总额 - 已结算 | 计算派生值 |
| One2many 展开 | `picking.move_ids` 在 Tree 内展示明细行 | 主从关系 |
| Smart Button | PO → 查看入库单 | 跨单据导航 |

---

## 五、与前版对比的主要修正

| 前版错误 | 修正说明 |
|----------|----------|
| 引用不存在的 `wms.shipment` 模型 | 确认正确模型为 `stock.picking` + `erp_source_type` |
| 供应商 `buyer_id` 标为新建 | 实际在 `purchase` 标准模块已有 |
| 银行信息标为缺失 | 实际通过 `res.partner.bank` One2many 覆盖 |
| 出库单覆盖率虚高 | 修正：`logistics.dispatch.waybill` 有大量字段但缺价格 |
| 未区分"跨表覆盖" | 本版明确标注哪些字段通过关联获取 |
