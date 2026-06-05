# 仓库 PDA 交互流程分析

> 版本: v1.0
> 日期: 2026-06-04
> 目的: 梳理仓库 PDA 与 Odoo WMS 的交互流程，明确已有能力与差距

---

## 一、现有 Odoo WMS 模块能力评估

### 1.1 wms_task_core 模块概况

`wms_task_core` 是一套 **任务状态机骨架**，覆盖收货→上架→出库→拣货→复核→交接完整链路定义。

### 1.2 功能成熟度

| 功能 | 模型 | 实现深度 |
|------|------|----------|
| 库位元数据扩展 | `stock.location` | ✅ 用途分类 + 拣货路径 + 暂存/交接区 |
| 库位绑定（产品固定库位） | — | ❌ 无 |
| 收货任务 | `wms.receipt.task` | ✅ 状态流转完整，自动从 picking 创建 |
| 上架任务 | `wms.putaway.task` | ⚠️ 有 dest_location_id 字段，不移动库存 |
| 出库任务 | `wms.outbound.task` | ✅ 自动创建 + 反写 sale.wms_status |
| 拣货任务 | `wms.pick.task` + `.line` | ⚠️ 从 move 生成行，不扣库存 |
| 复核任务 | `wms.check.task` | ⚠️ 仅状态流转 |
| 交接单 | `wms.handover.order` | ⚠️ 关联 TMS，不驱动装车库存 |
| 盘点/退库 | `wms.inventory.operation` | ✅ 可调 stock.quant；退库可生成 picking |
| 库存台账 | `wms.inventory.ledger` | ✅ SQL 视图，只读 |
| PDA/条码扫描 | — | ❌ 无 |
| 波次拣货集成 | `stock_picking_batch` | ❌ 依赖声明但未用 |
| stock.move.line 扩展 | — | ❌ 无 |

### 1.3 stock.picking 扩展字段

```
erp_source_type: sale/purchase/sale_return/purchase_return/internal
wms_flow_stage: WMS 出库任务状态
tms_handover_status: TMS 交接状态
store_partner_id: 门店
wms_task_ref: WMS 任务号引用
```

### 1.4 stock.location 扩展字段

```
location_usage_type_ext: pick_face/bulk/staging/handover/count_zone
pick_path_sequence: 拣货路径排序
is_staging_zone: 暂存区标记
is_handover_zone: 交接区标记
```

---

## 二、四大业务流程

### 2.1 入库操作（收货 + 上架 + 数量统计）

**触发**：采购单确认/补货到仓 → stock.picking(incoming) → wms.receipt.task

**PDA 操作步骤**：
1. 扫描到货单号/PO 号
2. 逐行扫描商品条码
3. 输入/确认实际到货数量
4. 确认收货完成
5. 系统自动创建上架任务
6. 扫描商品 → 扫描目标库位 → 确认上架数量
7. 绑定商品-库位关系
8. 确认上架完成 → 真实库存移动

**Odoo 模型映射**：
- 收货：`wms.receipt.task` + `stock.move.quantity_done`
- 上架：`wms.putaway.task` → `stock.move`（暂存区→目标库位）
- 绑定：`stock.putaway.rule` 或自定义

### 2.2 出库操作（拣货 + 放排线 + 数量统计）

**触发**：销售确认 → stock.picking(outgoing) → wms.outbound.task → wms.pick.task

**PDA 操作步骤**：
1. 扫描拣货任务号
2. 系统显示：商品+需求数量+库位（按路径排序）
3. 导航到库位 → 扫描库位码确认
4. 扫描商品码 → 输入实际拣货数量
5. 所有行拣完后 → 扫描排线库位码
6. 确认放置完成
7. 系统扣减库存 → 进入复核

**Odoo 模型映射**：
- 任务信息：`wms.pick.task.line`（product_id/demand_qty/source_location_id）
- 路径排序：`stock.location.pick_path_sequence`
- 实际数量：`pick.task.line.done_qty` → 回写 `stock.move.line`
- 排线库位：`stock.location.is_staging_zone`

### 2.3 补货退货操作

**触发**：补货多了/不好卖 → 选择退库类型

**PDA 操作步骤**：
1. 选择退库类型（warehouse_return）
2. 扫描商品条码 + 输入退货数量
3. 选择退货原因
4. 确认提交

**Odoo 模型映射**：
- `wms.inventory.operation`（type=warehouse_return）→ 自动生成内部 picking
- ✅ 此流程模型层基本完整

### 2.4 客户退货入库

**触发**：销售退货单确认 → stock.picking(incoming, sale_return) → wms.receipt.task

**PDA 操作步骤**：
1. 扫描退货入库单号
2. 逐行扫描退回商品 + 核对数量
3. 检查商品状态（完好/损坏）
4. 确认收货完成
5. 分流上架（完好→正常库位，损坏→退货处理区）

---

## 三、能力差距总结

| 功能模块 | 已有 | 需补充 | 优先级 |
|----------|------|--------|--------|
| 收货任务创建与状态 | ✅ | PDA 扫描接口 | 高 |
| 收货数量回写 | ⚠️ | 扫码→quantity_done+validate | 高 |
| 上架移库 | ⚠️ 骨架 | 创建 internal move、移动 quant | 高 |
| 产品-库位绑定 | ❌ | putaway rule 或自定义表 | 中 |
| 库位推荐 | ❌ | 基于规则+现有库存推荐 | 中 |
| 拣货任务获取 | ✅ | PDA 接口+路径排序 | 高 |
| 拣货数量确认 | ⚠️ | 回写 stock.move.line+扣减 | 高 |
| 放排线库位 | ⚠️ 有标记 | 创建 staging move | 中 |
| 退库操作 | ✅ | PDA 扫描入口 | 中 |
| 退货入库 | ⚠️ 设计中 | Sprint 3 后+PDA接口 | 中 |
| 品质检验(退货) | ❌ | 品质字段+分流逻辑 | 低 |
| 条码解析 | ❌ | 商品码/库位码/任务码统一解析 | 高 |
| PDA 用户认证 | ❌ | JWT/Session+仓库权限 | 高 |

---

## 四、PDA 功能模块设计

### 4.1 功能菜单

| 模块 | 功能 | 对应 API |
|------|------|---------|
| 入库收货 | 扫码收货+确认数量 | /api/wms/receipt/* |
| 上架作业 | 扫码上架+库位绑定 | /api/wms/putaway/* |
| 拣货任务 | 按路径拣货+数量 | /api/wms/pick/* |
| 退库操作 | 补货退货提交 | /api/wms/return/* |
| 退货收货 | 客户退货入库 | /api/wms/receipt/* (sale_return) |
| 库存查询 | 按商品/库位查库存 | /api/wms/inventory/query |
| 盘点作业 | 盘点+差异确认 | /api/wms/inventory/count |

### 4.2 需补充的三大层面

1. **库存事务层**：上架/拣货的真实 stock.move/stock.quant 操作
2. **PDA 接口层**：RESTful API 或 JSON-RPC Controller
3. **扫码解析层**：商品条码/库位条码/任务条码的统一解析
