from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class B2bCartDraft(models.Model):
    _name = "b2b.cart.draft"
    _description = "B2B 购物车草稿"
    _order = "write_date desc"

    partner_id = fields.Many2one("res.partner", string="客户", required=True)
    store_id = fields.Many2one("res.partner", string="收货门店")
    state = fields.Selection(
        [("draft", "草稿"), ("submitted", "已提交"), ("converted", "已转订单")],
        string="状态", default="draft",
    )
    line_ids = fields.One2many("b2b.cart.draft.line", "cart_id", string="明细")
    total_amount = fields.Float(string="合计金额", compute="_compute_total", store=True)
    total_qty = fields.Float(string="合计数量", compute="_compute_total", store=True)

    @api.depends("line_ids.qty", "line_ids.subtotal")
    def _compute_total(self):
        for c in self:
            c.total_qty = sum(l.qty for l in c.line_ids)
            c.total_amount = sum(l.subtotal for l in c.line_ids)

    def action_convert_to_sale_order(
        self,
        store_id=False,
        payment_method="credit",
        note="",
        submit_user_id=False,
        delivery_time_required="",
        **kwargs,
    ):
        """兼容旧下单入口，把购物车草稿转换成 B2B 销售订单。"""
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(_("购物车为空，不能提交订单。"))
        store_id = store_id or kwargs.get("store_partner_id") or kwargs.get("store_id")
        payment_method = payment_method or kwargs.get("b2b_payment_method") or "credit"
        note = note or kwargs.get("b2b_submit_note") or kwargs.get("submit_note") or ""
        submit_user_id = submit_user_id or kwargs.get("b2b_submit_user_id") or kwargs.get("user_id")
        submit_user = kwargs.get("submit_user")
        if submit_user and hasattr(submit_user, "id"):
            submit_user_id = submit_user.id
        delivery_time_required = delivery_time_required or kwargs.get("delivery_time") or kwargs.get("delivery_time_required") or ""
        store = kwargs.get("store")
        if store and hasattr(store, "exists"):
            store = store.sudo().exists()
        elif store:
            store = self.env["res.partner"].sudo().browse(store).exists()
        else:
            store = self.env["res.partner"].sudo().browse(store_id).exists() if store_id else self.store_id
        if not store:
            raise ValidationError(_("请选择收货门店。"))
        self.write({"state": "submitted", "store_id": store.id})
        try:
            order = self.env["sale.order"].sudo().create(
                {
                    "partner_id": self.partner_id.id,
                    "source_channel": "b2b",
                    "store_partner_id": store.id,
                    "b2b_payment_method": payment_method or "credit",
                    "b2b_submit_note": note or "",
                    "b2b_submit_user_id": submit_user_id or self.env.uid,
                    "delivery_time_required": delivery_time_required or "",
                    "pricelist_id": False,
                }
            )
            for line in self.line_ids:
                product = line.product_id.product_variant_id or line.product_id.product_variant_ids[:1]
                if not product:
                    raise ValidationError(_("商品 %s 没有可销售规格。") % line.product_id.display_name)
                order_line = self.env["sale.order.line"].sudo().create(
                    {
                        "order_id": order.id,
                        "product_template_id": line.product_id.id,
                        "product_id": product.id,
                        "product_uom_qty": line.qty,
                        "tax_ids": [(5, 0, 0)],
                    }
                )
                order_line.sudo().write({"price_unit": line.unit_price, "tax_ids": [(5, 0, 0)]})
            self.write({"state": "converted"})
            return order
        except Exception:
            self.write({"state": "draft"})
            raise


class B2bCartDraftLine(models.Model):
    _name = "b2b.cart.draft.line"
    _description = "B2B 购物车明细"

    cart_id = fields.Many2one("b2b.cart.draft", string="购物车", ondelete="cascade")
    product_id = fields.Many2one("product.template", string="商品", required=True)
    qty = fields.Float(string="数量", default=1.0)
    unit_price = fields.Float(string="单价")
    subtotal = fields.Float(string="小计", compute="_compute_subtotal", store=True)

    @api.depends("qty", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.unit_price
