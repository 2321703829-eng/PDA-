# 采购退货单模块设计

> 模块名: `erp_purchase_return`
> 优先级: P0
> 状态: 设计中

---

## 1. 模块结构

```
erp_purchase_return/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── purchase_return.py          # 采购退货单主表
│   └── purchase_return_line.py     # 采购退货单明细行
├── views/
│   ├── purchase_return_views.xml
│   └── purchase_return_line_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── purchase_return_security.xml
├── data/
│   └── sequence_data.xml
└── static/
    └── description/
        └── icon.png
```

---

## 2. 数据模型设计

### 2.1 主表: `erp.purchase.return`

| 字段名 | 类型 | 必填 | 说明 | 对应 ERP 模板 |
|--------|------|------|------|---------------|
| `name` | Char | ✅ | 退货单号（自动生成） | 单据号 |
| `date` | Date | ✅ | 退货日期 | 单据日期 |
| `company_id` | Many2one | ✅ | 所属组织 | 所属组织 |
| `warehouse_id` | Many2one | ✅ | 仓库 | 仓库 |
| `partner_id` | Many2one | ✅ | 供应商 | 供应商名称 |
| `partner_ref` | Char | — | 供应商编号 | 供应商编号 |
| `buyer_id` | Many2one | — | 采购员 | 采购员 |
| `return_reason` | Selection | — | 退货原因 | 退货原因 |
| `state` | Selection | ✅ | 状态 | 状态 |
| `line_ids` | One2many | ✅ | 明细行 | — |
| `amount_total` | Float | — | 退货金额合计 | 金额 |
| `picking_ids` | One2many | — | 关联出库单 | — |
| `origin` | Char | — | 原入库单号 | 原入库单号 |
| `note` | Text | — | 备注 | 备注 |
| `create_uid` | Many2one | — | 创建人 | 创建人 |
| `create_date` | Datetime | — | 创建日期 | 创建日期 |
| `write_uid` | Many2one | — | 审核人 | 审核人 |
| `write_date` | Datetime | — | 审核日期 | 审核日期 |

**状态流转**:
```
草稿 → 已提交 → 已审核 → 已完成
                  ↓
               已取消
```

---

### 2.2 明细行: `erp.purchase.return.line`

| 字段名 | 类型 | 必填 | 说明 | 对应 ERP 模板 |
|--------|------|------|------|---------------|
| `return_id` | Many2one | ✅ | 关联退货单 | — |
| `product_id` | Many2one | ✅ | 商品 | 商品编号/名称 |
| `product_code` | Char | — | 商品编号 | 商品编号 |
| `product_name` | Char | — | 商品名称 | 商品名称 |
| `barcode` | Char | — | 条形码 | 条形码 |
| `spec_desc` | Char | — | 规格 | 规格 |
| `product_uom` | Many2one | ✅ | 单位 | 单位 |
| `quantity` | Float | ✅ | 数量 | 数量 |
| `price_unit` | Float | ✅ | 单价 | 单价 |
| `price_subtotal` | Float | — | 金额 | 金额 |
| `lot_id` | Many2one | — | 批次号 | 批次号 |
| `production_date` | Date | — | 生产日期 | 生产日期 |
| `expiration_date` | Date | — | 保质期 | 保质期 |
| `is_gift` | Boolean | — | 是否赠品 | 是否赠品 |
| `note` | Char | — | 备注 | 明细备注 |

---

## 3. 关联关系

### 3.1 与采购订单的关联
- 退货单可关联原采购订单（通过 `purchase_order_id`）
- 退货明细可关联原采购订单行（通过 `purchase_order_line_id`）

### 3.2 与入库单的关联
- 退货单可关联原入库单（通过 `picking_id`）
- 用于追溯退货来源

### 3.3 与库存的关联
- 退货审核后自动生成 `stock.picking`（类型：退货出库）
- 更新库存数量

---

## 4. 业务流程

```
1. 创建退货单
   - 选择供应商
   - 选择退货商品（可从入库单选择）
   - 填写退货数量、原因

2. 提交审核
   - 状态: 草稿 → 已提交

3. 审核通过
   - 状态: 已提交 → 已审核
   - 自动生成退货出库单（stock.picking）

4. 退货出库
   - 状态: 已审核 → 已完成
   - 更新库存

5. 取消
   - 状态: 已提交/已审核 → 已取消
```

---

## 5. 技术实现要点

### 5.1 自动生成单号
```python
@api.model
def create(self, vals):
    if vals.get('name', 'New') == 'New':
        vals['name'] = self.env['ir.sequence'].next_by_code('erp.purchase.return') or 'New'
    return super().create(vals)
```

### 5.2 金额计算
```python
@api.depends('line_ids.price_subtotal')
def _compute_amount_total(self):
    for record in self:
        record.amount_total = sum(record.line_ids.mapped('price_subtotal'))
```

### 5.3 自动生成退货出库单
```python
def action_approve(self):
    # 创建 stock.picking
    picking_type = self.env['stock.picking.type'].search([
        ('code', '=', 'outgoing'),
        ('warehouse_id', '=', self.warehouse_id.id)
    ], limit=1)
    
    picking = self.env['stock.picking'].create({
        'picking_type_id': picking_type.id,
        'partner_id': self.partner_id.id,
        'origin': self.name,
        # ...
    })
    
    # 创建 stock.move
    for line in self.line_ids:
        self.env['stock.move'].create({
            'picking_id': picking.id,
            'product_id': line.product_id.id,
            'product_uom_qty': line.quantity,
            # ...
        })
    
    self.write({'state': 'approved', 'picking_ids': [(4, picking.id)]})
```

---

## 6. 视图设计

### 6.1 表单视图
- 主表信息区域
- 明细行 Tab
- 关联单据 Tab
- 备注 Tab

### 6.2 列表视图
- 单据号、日期、供应商、状态、金额

### 6.3 搜索视图
- 按单据号、供应商、状态、日期筛选

---

## 7. 权限设计

| 角色 | 权限 |
|------|------|
| 采购员 | 创建、编辑、提交 |
| 采购主管 | 审核、取消 |
| 仓库管理员 | 查看、执行退货出库 |

---

## 8. 与其他模块的集成

### 8.1 与 `erp_base` 的集成
- 使用 `erp_base` 的基础字段（公司、仓库、供应商等）
- 继承 `erp_base` 的审批流程

### 8.2 与 `wms_task_core` 的集成
- 退货审核后自动生成 WMS 任务
- 更新库存台账

### 8.3 与 `logistics_base` 的集成
- 使用商品、供应商等基础数据

---

## 9. 实施计划

| 阶段 | 任务 | 工作量 | 状态 |
|------|------|--------|------|
| 1 | 模型定义 | 2h | ⏳ 待开始 |
| 2 | 视图开发 | 3h | ⏳ 待开始 |
| 3 | 权限配置 | 1h | ⏳ 待开始 |
| 4 | 业务逻辑 | 4h | ⏳ 待开始 |
| 5 | 测试 | 2h | ⏳ 待开始 |
| 6 | 文档 | 1h | ⏳ 待开始 |

**总计**: 13h

---

## 10. 验收标准

- [ ] 能创建采购退货单
- [ ] 能添加明细行（商品、数量、单价）
- [ ] 能自动计算金额
- [ ] 能审核并生成退货出库单
- [ ] 能更新库存
- [ ] 能查看关联单据
- [ ] 能导出报表
