# 结算体系模块设计

> 模块名: `erp_settlement`
> 优先级: P0
> 状态: 设计中

---

## 1. 现状分析

### 1.1 现有模型
- ❌ 无独立结算模型
- ❌ 各单据无结算字段
- ❌ 无对账功能

### 1.2 ERP 模板要求
- 采购订单：已结算金额、未结算金额、结算状态
- 采购入库单：已结算金额、未结算金额、结算状态
- 采购退货单：已结算金额、未结算金额、结算状态
- 销售订单：已结算金额、未结算金额、结算状态
- 销售出库单：已结算金额、未结算金额、结算状态
- 销售退货单：已结算金额、未结算金额、结算状态

---

## 2. 模块结构

```
erp_settlement/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── settlement.py               # 结算单主表
│   ├── settlement_line.py          # 结算单明细行
│   ├── purchase_order_ext.py       # 采购订单扩展
│   ├── sale_order_ext.py           # 销售订单扩展
│   └── stock_picking_ext.py        # 出入库单扩展
├── views/
│   ├── settlement_views.xml
│   └── settlement_line_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── settlement_security.xml
├── data/
│   └── sequence_data.xml
└── static/
    └── description/
        └── icon.png
```

---

## 3. 数据模型设计

### 3.1 结算单主表: `erp.settlement`

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | Char | ✅ | 结算单号（自动生成） |
| `date` | Date | ✅ | 结算日期 |
| `company_id` | Many2one | ✅ | 所属组织 |
| `partner_id` | Many2one | ✅ | 客户/供应商 |
| `settlement_type` | Selection | ✅ | 结算类型（采购/销售） |
| `amount_total` | Float | ✅ | 结算金额 |
| `amount_paid` | Float | — | 已付金额 |
| `amount_residual` | Float | — | 未付金额 |
| `state` | Selection | ✅ | 状态 |
| `line_ids` | One2many | ✅ | 明细行 |
| `note` | Text | — | 备注 |

**结算类型**:
- 采购结算：关联采购订单/入库单/退货单
- 销售结算：关联销售订单/出库单/退货单

**状态流转**:
```
草稿 → 已提交 → 已审核 → 已完成
                  ↓
               已取消
```

---

### 3.2 结算明细行: `erp.settlement.line`

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `settlement_id` | Many2one | ✅ | 关联结算单 |
| `source_type` | Selection | ✅ | 来源类型 |
| `source_id` | Many2one | ✅ | 来源单据 |
| `amount` | Float | ✅ | 结算金额 |
| `note` | Char | — | 备注 |

**来源类型**:
- 采购订单
- 采购入库单
- 采购退货单
- 销售订单
- 销售出库单
- 销售退货单

---

## 4. 单据扩展

### 4.1 采购订单扩展
```python
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    settlement_line_ids = fields.One2many('erp.settlement.line', 'source_id', 
                                          string='结算明细', 
                                          domain=[('source_type', '=', 'purchase_order')])
    amount_settled = fields.Float(string='已结算金额', compute='_compute_settlement')
    amount_residual = fields.Float(string='未结算金额', compute='_compute_settlement')
    settlement_state = fields.Selection([
        ('unsettled', '未结算'),
        ('partial', '部分结算'),
        ('settled', '全部结算'),
    ], string='结算状态', compute='_compute_settlement')
    
    @api.depends('settlement_line_ids.amount')
    def _compute_settlement(self):
        for order in self:
            settled = sum(order.settlement_line_ids.mapped('amount'))
            order.amount_settled = settled
            order.amount_residual = order.amount_total - settled
            if settled == 0:
                order.settlement_state = 'unsettled'
            elif settled >= order.amount_total:
                order.settlement_state = 'settled'
            else:
                order.settlement_state = 'partial'
```

### 4.2 销售订单扩展
```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    settlement_line_ids = fields.One2many('erp.settlement.line', 'source_id',
                                          string='结算明细',
                                          domain=[('source_type', '=', 'sale_order')])
    amount_settled = fields.Float(string='已结算金额', compute='_compute_settlement')
    amount_residual = fields.Float(string='未结算金额', compute='_compute_settlement')
    settlement_state = fields.Selection([
        ('unsettled', '未结算'),
        ('partial', '部分结算'),
        ('settled', '全部结算'),
    ], string='结算状态', compute='_compute_settlement')
```

### 4.3 出入库单扩展
```python
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    settlement_line_ids = fields.One2many('erp.settlement.line', 'source_id',
                                          string='结算明细')
    amount_settled = fields.Float(string='已结算金额', compute='_compute_settlement')
    amount_residual = fields.Float(string='未结算金额', compute='_compute_settlement')
    settlement_state = fields.Selection([
        ('unsettled', '未结算'),
        ('partial', '部分结算'),
        ('settled', '全部结算'),
    ], string='结算状态', compute='_compute_settlement')
```

---

## 5. 业务流程

### 5.1 采购结算流程
```
1. 创建采购结算单
   - 选择供应商
   - 选择要结算的采购单据（订单/入库单/退货单）
   - 填写结算金额

2. 提交审核
   - 状态: 草稿 → 已提交

3. 审核通过
   - 状态: 已提交 → 已审核
   - 更新各单据的结算字段

4. 完成
   - 状态: 已审核 → 已完成
```

### 5.2 销售结算流程
```
1. 创建销售结算单
   - 选择客户
   - 选择要结算的销售单据（订单/出库单/退货单）
   - 填写结算金额

2. 提交审核
   - 状态: 草稿 → 已提交

3. 审核通过
   - 状态: 已提交 → 已审核
   - 更新各单据的结算字段

4. 完成
   - 状态: 已审核 → 已完成
```

---

## 6. 实施计划

| 阶段 | 任务 | 工作量 | 状态 |
|------|------|--------|------|
| 1 | 结算单模型 | 3h | ⏳ 待开始 |
| 2 | 单据扩展 | 4h | ⏳ 待开始 |
| 3 | 视图开发 | 3h | ⏳ 待开始 |
| 4 | 业务逻辑 | 4h | ⏳ 待开始 |
| 5 | 测试 | 3h | ⏳ 待开始 |
| 6 | 文档 | 1h | ⏳ 待开始 |

**总计**: 18h

---

## 7. 验收标准

- [ ] 能创建采购结算单
- [ ] 能创建销售结算单
- [ ] 能关联多个单据进行结算
- [ ] 能自动更新各单据的结算字段
- [ ] 能查看结算明细
- [ ] 能导出结算报表
