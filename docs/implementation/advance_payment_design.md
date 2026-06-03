# 预付款体系模块设计

> 模块名: `erp_advance_payment`（或集成到 `erp_settlement`）
> 优先级: P1
> 状态: 设计中

---

## 1. 现状分析

### 1.1 现有模型
- ❌ 无独立预付款模型
- ❌ 采购订单无预付字段
- ❌ 无预付审批流程

### 1.2 ERP 模板要求
- 预付款审核状态
- 预付状态
- 累计预付金额
- 付款单号

---

## 2. 模块结构

```
erp_advance_payment/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── advance_payment.py          # 预付款单主表
│   ├── advance_payment_line.py     # 预付款单明细行
│   └── purchase_order_ext.py       # 采购订单扩展
├── views/
│   ├── advance_payment_views.xml
│   └── advance_payment_line_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── advance_payment_security.xml
├── data/
│   └── sequence_data.xml
└── static/
    └── description/
        └── icon.png
```

---

## 3. 数据模型设计

### 3.1 预付款单主表: `erp.advance.payment`

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | Char | ✅ | 预付款单号（自动生成） |
| `date` | Date | ✅ | 预付日期 |
| `company_id` | Many2one | ✅ | 所属组织 |
| `partner_id` | Many2one | ✅ | 供应商 |
| `purchase_order_id` | Many2one | ✅ | 关联采购订单 |
| `amount` | Float | ✅ | 预付金额 |
| `state` | Selection | ✅ | 状态 |
| `payment_method` | Selection | — | 付款方式 |
| `bank_account` | Char | — | 收款账号 |
| `note` | Text | — | 备注 |

**状态流转**:
```
草稿 → 已提交 → 已审核 → 已付款
                  ↓
               已取消
```

---

### 3.2 采购订单扩展
```python
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    advance_payment_ids = fields.One2many('erp.advance.payment', 'purchase_order_id',
                                          string='预付款记录')
    advance_payment_state = fields.Selection([
        ('none', '未预付'),
        ('partial', '部分预付'),
        ('full', '全部预付'),
    ], string='预付状态', compute='_compute_advance_payment')
    advance_payment_amount = fields.Float(string='累计预付金额', 
                                          compute='_compute_advance_payment')
    
    @api.depends('advance_payment_ids.amount', 'advance_payment_ids.state')
    def _compute_advance_payment(self):
        for order in self:
            paid = sum(order.advance_payment_ids.filtered(
                lambda p: p.state == 'paid').mapped('amount'))
            order.advance_payment_amount = paid
            if paid == 0:
                order.advance_payment_state = 'none'
            elif paid >= order.amount_total:
                order.advance_payment_state = 'full'
            else:
                order.advance_payment_state = 'partial'
```

---

## 4. 业务流程

```
1. 创建预付款单
   - 选择采购订单
   - 填写预付金额
   - 选择付款方式

2. 提交审核
   - 状态: 草稿 → 已提交

3. 审核通过
   - 状态: 已提交 → 已审核

4. 付款完成
   - 状态: 已审核 → 已付款
   - 更新采购订单的预付字段

5. 取消
   - 状态: 已提交/已审核 → 已取消
```

---

## 5. 实施计划

| 阶段 | 任务 | 工作量 | 状态 |
|------|------|--------|------|
| 1 | 预付款单模型 | 2h | ⏳ 待开始 |
| 2 | 采购订单扩展 | 1h | ⏳ 待开始 |
| 3 | 视图开发 | 2h | ⏳ 待开始 |
| 4 | 业务逻辑 | 3h | ⏳ 待开始 |
| 5 | 测试 | 2h | ⏳ 待开始 |
| 6 | 文档 | 1h | ⏳ 待开始 |

**总计**: 11h

---

## 6. 验收标准

- [ ] 能创建预付款单
- [ ] 能关联采购订单
- [ ] 能审核并标记为已付款
- [ ] 能自动更新采购订单的预付字段
- [ ] 能查看预付明细
- [ ] 能导出预付报表
