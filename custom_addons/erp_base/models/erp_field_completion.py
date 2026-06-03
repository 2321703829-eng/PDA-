from odoo import api, fields, models


class ErpSettlementMixin(models.AbstractModel):
    _name = "erp.settlement.mixin"
    _description = "ERP Settlement Fields Mixin"

    erp_currency_id = fields.Many2one(
        "res.currency",
        string="结算币种",
        compute="_compute_erp_currency_id",
    )
    amount_settled = fields.Monetary(
        string="已结算金额",
        default=0.0,
        currency_field="erp_currency_id",
    )
    amount_unsettled = fields.Monetary(
        string="未结算金额",
        compute="_compute_erp_settlement_amounts",
        store=True,
        currency_field="erp_currency_id",
    )
    settlement_state = fields.Selection(
        [
            ("unsettled", "未结算"),
            ("partial", "部分结算"),
            ("settled", "已结算"),
        ],
        string="结算状态",
        compute="_compute_erp_settlement_amounts",
        store=True,
        default="unsettled",
    )

    def _get_erp_settlement_total(self):
        self.ensure_one()
        if "amount_total" in self._fields:
            return self.amount_total or 0.0
        return 0.0

    @api.depends("company_id")
    def _compute_erp_currency_id(self):
        for record in self:
            currency = False
            if "currency_id" in record._fields and record.currency_id:
                currency = record.currency_id
            elif "company_id" in record._fields and record.company_id:
                currency = record.company_id.currency_id
            record.erp_currency_id = currency or record.env.company.currency_id

    @api.depends("amount_settled", "amount_total")
    def _compute_erp_settlement_amounts(self):
        for record in self:
            total = record._get_erp_settlement_total()
            settled = record.amount_settled or 0.0
            record.amount_unsettled = max(total - settled, 0.0)
            if settled <= 0:
                record.settlement_state = "unsettled"
            elif settled < total:
                record.settlement_state = "partial"
            else:
                record.settlement_state = "settled"


class PurchaseOrderErpCompletion(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "erp.settlement.mixin"]

    order_type = fields.Selection(
        [
            ("standard", "标准采购"),
            ("return", "采购退货"),
        ],
        string="采购类型",
        default="standard",
        required=True,
        index=True,
    )
    return_reason = fields.Text(string="退货原因")
    source_picking_id = fields.Many2one(
        "stock.picking",
        string="原入库单",
        ondelete="set null",
    )
    source_order_id = fields.Many2one(
        "purchase.order",
        string="原采购订单",
        ondelete="set null",
    )
    department_id = fields.Many2one("hr.department", string="部门")
    approval_user_id = fields.Many2one("res.users", string="审核人")
    approval_date = fields.Datetime(string="审核日期")
    advance_payment_ids = fields.Many2many(
        "account.payment",
        "erp_purchase_order_advance_payment_rel",
        "purchase_order_id",
        "payment_id",
        string="关联预付款单",
    )
    advance_payment_state = fields.Selection(
        [
            ("none", "无预付"),
            ("to_review", "待审核"),
            ("approved", "已审核"),
        ],
        string="预付款状态",
        compute="_compute_advance_payment_summary",
        store=True,
    )
    advance_payment_amount = fields.Monetary(
        string="累计预付金额",
        compute="_compute_advance_payment_summary",
        store=True,
        currency_field="currency_id",
    )
    advance_payment_number = fields.Char(
        string="付款单号汇总",
        compute="_compute_advance_payment_summary",
        store=True,
    )

    @api.depends("advance_payment_ids", "advance_payment_ids.amount", "advance_payment_ids.state")
    def _compute_advance_payment_summary(self):
        for order in self:
            payments = order.advance_payment_ids
            order.advance_payment_amount = sum(payments.mapped("amount"))
            order.advance_payment_number = ", ".join(payments.mapped("name"))
            if not payments:
                order.advance_payment_state = "none"
            elif any(payment.state not in ("paid", "posted", "reconciled") for payment in payments):
                order.advance_payment_state = "to_review"
            else:
                order.advance_payment_state = "approved"


class SaleOrderErpCompletion(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "erp.settlement.mixin"]

    department_id = fields.Many2one("hr.department", string="部门")
    approval_user_id = fields.Many2one("res.users", string="审核人")
    approval_date = fields.Datetime(string="审核日期")
    advance_receipt_ids = fields.Many2many(
        "account.payment",
        "erp_sale_order_advance_receipt_rel",
        "sale_order_id",
        "payment_id",
        string="关联预收款单",
    )
    advance_receipt_state = fields.Selection(
        [
            ("none", "无预收"),
            ("to_review", "待审核"),
            ("approved", "已审核"),
        ],
        string="预收款状态",
        compute="_compute_advance_receipt_summary",
        store=True,
    )
    advance_receipt_amount = fields.Monetary(
        string="累计预收金额",
        compute="_compute_advance_receipt_summary",
        store=True,
        currency_field="currency_id",
    )

    @api.depends("advance_receipt_ids", "advance_receipt_ids.amount", "advance_receipt_ids.state")
    def _compute_advance_receipt_summary(self):
        for order in self:
            payments = order.advance_receipt_ids
            order.advance_receipt_amount = sum(payments.mapped("amount"))
            if not payments:
                order.advance_receipt_state = "none"
            elif any(payment.state not in ("paid", "posted", "reconciled") for payment in payments):
                order.advance_receipt_state = "to_review"
            else:
                order.advance_receipt_state = "approved"


class StockPickingErpCompletion(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "erp.settlement.mixin"]

    sale_return_id = fields.Many2one(
        "erp.sale.return",
        string="销售退货单",
        ondelete="set null",
    )
    recovery_status = fields.Selection(
        [
            ("pending", "待回收"),
            ("recovered", "已回收"),
            ("not_applicable", "不适用"),
        ],
        string="回收状态",
        default="not_applicable",
    )
    amount_total = fields.Monetary(
        string="单据金额",
        compute="_compute_erp_picking_amount_total",
        store=True,
        currency_field="erp_currency_id",
    )

    @api.depends("move_ids.sale_price_subtotal", "move_ids.purchase_price_subtotal")
    def _compute_erp_picking_amount_total(self):
        for picking in self:
            picking.amount_total = sum(
                move.sale_price_subtotal or move.purchase_price_subtotal
                for move in picking.move_ids
            )


class StockMoveErpCompletion(models.Model):
    _inherit = "stock.move"

    sale_price_unit = fields.Float(string="销售单价")
    sale_price_subtotal = fields.Float(
        string="销售金额",
        compute="_compute_erp_price_subtotals",
        store=True,
    )
    purchase_price_unit = fields.Float(string="采购单价")
    purchase_price_subtotal = fields.Float(
        string="采购金额",
        compute="_compute_erp_price_subtotals",
        store=True,
    )

    @api.depends("quantity", "sale_price_unit", "purchase_price_unit")
    def _compute_erp_price_subtotals(self):
        for move in self:
            qty = move.quantity or 0.0
            move.sale_price_subtotal = qty * (move.sale_price_unit or 0.0)
            move.purchase_price_subtotal = qty * (move.purchase_price_unit or 0.0)


class StockWarehouseOrderpointErpCompletion(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    fixed_purchase_qty = fields.Float(string="固定采购量")
    replenishment_strategy = fields.Selection(
        [
            ("min_max", "安全库存补货"),
            ("fixed", "固定采购量"),
            ("forecast", "预测补货"),
            ("manual", "手工补货"),
        ],
        string="补货策略",
        default="min_max",
    )
    forecast_method = fields.Char(string="预测方案")
    in_transit_qty = fields.Float(
        string="在途数量",
        compute="_compute_erp_orderpoint_quantities",
        store=False,
    )
    on_hand_qty = fields.Float(
        string="在库数量",
        compute="_compute_erp_orderpoint_quantities",
        store=False,
    )
    suggested_purchase_qty = fields.Float(
        string="建议采购量",
        compute="_compute_erp_orderpoint_quantities",
        store=False,
    )

    def _compute_erp_orderpoint_quantities(self):
        for orderpoint in self:
            product = orderpoint.product_id
            orderpoint.on_hand_qty = product.qty_available if product else 0.0
            orderpoint.in_transit_qty = 0.0
            if orderpoint.replenishment_strategy == "fixed":
                orderpoint.suggested_purchase_qty = orderpoint.fixed_purchase_qty
            else:
                target_qty = orderpoint.product_max_qty or orderpoint.product_min_qty or 0.0
                orderpoint.suggested_purchase_qty = max(target_qty - orderpoint.on_hand_qty, 0.0)


class ResPartnerErpSupplierCompletion(models.Model):
    _inherit = "res.partner"

    arrival_days = fields.Integer(string="到货天数")
    supplier_external_code = fields.Char(string="供应商金蝶外部编码", index=True)
    purchase_price_type = fields.Selection(
        [
            ("net", "净价"),
            ("tax_included", "含税价"),
            ("contract", "合同价"),
        ],
        string="采购价格类型",
    )


class ErpSaleReturnCompletion(models.Model):
    _name = "erp.sale.return"
    _inherit = ["erp.sale.return", "erp.settlement.mixin"]

    company_id = fields.Many2one(
        "res.company",
        string="组织",
        default=lambda self: self.env.company,
        required=True,
    )
    line_ids = fields.One2many(
        "erp.sale.return.line",
        "return_id",
        string="退货明细",
    )
    user_id = fields.Many2one("res.users", string="业务员")
    department_id = fields.Many2one("hr.department", string="部门")
    warehouse_id = fields.Many2one("stock.warehouse", string="仓库")
    source_shipment_no = fields.Char(string="源出库单号")
    delivery_method = fields.Selection(
        [
            ("self", "自提"),
            ("delivery", "配送"),
            ("third_party", "第三方配送"),
        ],
        string="配送方式",
    )
    route_name = fields.Char(string="线路")
    business_type = fields.Selection(
        [
            ("normal", "普通退货"),
            ("after_sale", "售后退货"),
            ("claim", "扣赔退货"),
        ],
        string="业务类型",
        default="normal",
    )
    approval_user_id = fields.Many2one("res.users", string="审核人")
    approval_date = fields.Datetime(string="审核日期")


class ErpSaleReturnLine(models.Model):
    _name = "erp.sale.return.line"
    _description = "销售退货明细行"
    _order = "return_id, id"

    return_id = fields.Many2one(
        "erp.sale.return",
        string="销售退货单",
        required=True,
        ondelete="cascade",
        index=True,
    )
    product_id = fields.Many2one("product.product", string="商品", required=True)
    product_uom = fields.Many2one("uom.uom", string="单位")
    qty = fields.Float(string="退货数量", default=1.0)
    qty_base = fields.Float(string="基本单位数量")
    price_unit = fields.Float(string="退货单价")
    price_subtotal = fields.Float(
        string="退货金额",
        compute="_compute_price_subtotal",
        store=True,
    )
    return_reason = fields.Char(string="行级退货原因")
    note = fields.Text(string="明细备注")

    @api.depends("qty", "price_unit")
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = (line.qty or 0.0) * (line.price_unit or 0.0)
