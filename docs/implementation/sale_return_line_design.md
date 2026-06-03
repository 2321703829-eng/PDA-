# 销售退货明细行模块设计

> 模块名: `erp_sale_return`（扩展现有模块）
> 优先级: P0
> 状态: 设计中

---

## 1. 现状分析

### 1.1 现有模型
```python
# erp_base/models/erp_sale_return.py
class ErpSaleReturn(models.Model):
    _name = 'erp.sale.return'
    _description = '销售退货单'
    
    name = fields.Char(string='退货单号')
    sale_order_id = fields.Many2one('sale.order', string='原销售订单')
    partner_id = fields.Many2one('res.partner', string='客户')
    return_date = fields.Date(string='退货日期')
    return_reason = fields.Selection([...], string='退货原因')
    state = fields.Selection([...], string='状态')
    amount_total = fields.Float(string='退货金额')
    picking_ids = fields.Many2many('stock.picking', string='关联入库单')
    refund_invoice_id = fields.Many2one('account.move', string='退款凭证')
    note = fields.Text(string='备注')
```

### 1.2 缺失内容
- ❌ 无明细行（`line_ids`）
- ❌ 无业务员、部门、仓库字段
- ❌ 无结算相关字段

---

## 2. 扩展方案

### 2.1 新增明细行模型: `erp.sale.return.line`

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

## 3. 扩展主表字段

### 3.1 新增字段
```python
# 在 erp_base/models/erp_sale_return.py 中添加
class ErpSaleReturn(models.Model):
    _inherit = 'erp.sale.return'
    
    # 新增字段
    line_ids = fields.One2many('erp.sale.return.line', 'return_id', string='明细行')
    company_id = fields.Many2one('res.company', string='所属组织')
    warehouse_id = fields.Many2one('stock.warehouse', string='仓库')
    department_id = fields.Many2one('hr.department', string='部门')
    user_id = fields.Many2one('res.users', string='业务员')
    route_id = fields.Many2one('logistics.route', string='线路')
    
    # 结算字段
    amount_settled = fields.Float(string='已结算金额')
    amount_residual = fields.Float(string='未结算金额')
    settlement_state = fields.Selection([...], string='结算状态')
    
    # 重新计算金额
    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.line_ids.mapped('price_subtotal'))
```

---

## 4. 关联关系

### 4.1 与销售订单的关联
- 退货单可关联原销售订单（通过 `sale_order_id`）
- 退货明细可关联原销售订单行（通过 `sale_order_line_id`）

### 4.2 与库存的关联
- 退货审核后自动生成 `stock.picking`（类型：退货入库）
- 更新库存数量

---

## 5. 业务流程

```
1. 创建退货单
   - 选择客户
   - 选择退货商品（可从销售订单选择）
   - 填写退货数量、原因

2. 提交审核
   - 状态: 草稿 → 已提交

3. 审核通过
   - 状态: 已提交 → 已审核
   - 自动生成退货入库单（stock.picking）

4. 退货入库
   - 状态: 已审核 → 已完成
   - 更新库存

5. 取消
   - 状态: 已提交/已审核 → 已取消
```

---

## 6. 实施计划

| 阶段 | 任务 | 工作量 | 状态 |
|------|------|--------|------|
| 1 | 新增明细行模型 | 2h | ⏳ 待开始 |
| 2 | 扩展主表字段 | 1h | ⏳ 待开始 |
| 3 | 视图开发 | 2h | ⏳ 待开始 |
| 4 | 业务逻辑 | 3h | ⏳ 待开始 |
| 5 | 测试 | 2h | ⏳ 待开始 |
| 6 | 文档 | 1h | ⏳ 待开始 |

**总计**: 11h

---

## 7. 验收标准

- [ ] 能创建销售退货单
- [ ] 能添加明细行（商品、数量、单价）
- [ ] 能自动计算金额
- [ ] 能审核并生成退货入库单
- [ ] 能更新库存
- [ ] 能查看关联单据
- [ ] 能导出报表
