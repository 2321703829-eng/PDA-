from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchWaybillCustomerGoodsLine(models.Model):
    _name = "logistics.dispatch.waybill.customer.goods.line"
    _description = "运单配送节点货物明细"
    _order = "sequence, id"

    _check_waybill_goods_nonnegative = models.Constraint(
        "check(quantity >= 0 and package_count >= 0 and weight >= 0 and volume >= 0)",
        "货物数量、件数、重量和体积不能小于 0。",
    )

    @api.model
    def get_import_templates(self):
        return [
            {
                "label": self.env._("下载标准模板（英文列头）"),
                "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V3&template_version=v3&template_locale=en_US",
            },
            {
                "label": self.env._("下载标准模板（中文列头）"),
                "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V3&template_version=v3&template_locale=zh_CN",
            },
        ]

    sequence = fields.Integer(string="排序", default=10)
    customer_line_id = fields.Many2one(
        "logistics.dispatch.waybill.customer.line",
        string="配送节点明细",
        required=True,
        ondelete="cascade",
        index=True,
    )
    order_line_id = fields.Many2one(
        "logistics.dispatch.waybill.order.line",
        string="订单行",
        ondelete="set null",
        index=True,
    )
    waybill_no = fields.Char(string="运单号（导入导出）", compute="_compute_waybill_no", inverse="_inverse_waybill_no")
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="运单",
        related="customer_line_id.waybill_id",
        store=True,
        readonly=True,
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="客户",
        related="customer_line_id.customer_id",
        store=True,
        readonly=True,
    )
    customer_no = fields.Char(string="客户号", compute="_compute_customer_no", inverse="_inverse_customer_no")
    customer_name = fields.Char(string="客户名称", compute="_compute_customer_name", inverse="_inverse_customer_name")
    partner_no = fields.Char(string="客户号（兼容）", compute="_compute_partner_fields", inverse="_inverse_partner_no")
    partner_name = fields.Char(string="客户名称（兼容）", compute="_compute_partner_fields", inverse="_inverse_partner_name")

    product_tmpl_id = fields.Many2one("product.template", string="商品主档", ondelete="set null")
    product_unit_id = fields.Many2one("logistics.product.unit", string="商品规格", ondelete="set null")
    external_product_code_snapshot = fields.Char(string="商品编码快照", size=64, index=True)
    product_name_snapshot = fields.Char(string="商品名称快照", size=128)
    spec_snapshot = fields.Char(string="规格快照", size=64)
    barcode_snapshot = fields.Char(string="条码快照", size=64)
    brand_name_snapshot = fields.Char(string="品牌快照", size=64)
    category_name_snapshot = fields.Char(string="类别快照", size=64)
    tag_name_snapshot = fields.Char(string="标签快照", size=64)
    base_unit_name = fields.Char(string="基础单位", size=32)
    doc_unit_name = fields.Char(string="单据单位", size=32)
    small_unit_name = fields.Char(string="小单位", size=32)
    base_qty = fields.Float(string="基础数量", digits=(16, 4), default=0.0)
    doc_qty = fields.Float(string="单据数量", digits=(16, 4), default=0.0)
    small_qty = fields.Float(string="小单位数量", digits=(16, 4), default=0.0)
    box_qty = fields.Float(string="箱数", digits=(16, 4), default=0.0)
    gift_qty = fields.Float(string="赠品数量", digits=(16, 4), default=0.0)
    exchange_qty = fields.Float(string="换货数量", digits=(16, 4), default=0.0)
    company_id = fields.Many2one("res.company", string="公司", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one("res.currency", string="币种", related="company_id.currency_id", store=True)
    unit_price = fields.Monetary(string="单价", currency_field="currency_id", default=0.0)
    small_unit_price = fields.Monetary(string="小单位单价", currency_field="currency_id", default=0.0)
    amount = fields.Monetary(string="金额", currency_field="currency_id", default=0.0)
    settled_amount = fields.Monetary(string="已结算金额", currency_field="currency_id", default=0.0)
    unsettled_amount = fields.Monetary(string="未结算金额", currency_field="currency_id", default=0.0)
    tax_amount = fields.Monetary(string="税额", currency_field="currency_id", default=0.0)
    amount_ex_tax = fields.Monetary(string="不含税金额", currency_field="currency_id", default=0.0)
    cost_amount = fields.Monetary(string="成本金额", currency_field="currency_id", default=0.0)
    gross_profit = fields.Monetary(string="毛利", currency_field="currency_id", default=0.0)
    gross_profit_rate = fields.Float(string="毛利率", digits=(8, 4), default=0.0)
    above_standard_price_flag = fields.Boolean(string="高于标准价", default=False)
    below_standard_price_flag = fields.Boolean(string="低于标准价", default=False)
    unit_weight = fields.Float(string="单件重量", digits=(16, 6), default=0.0)
    unit_volume = fields.Float(string="单件体积", digits=(16, 6), default=0.0)
    total_weight = fields.Float(string="总重量", digits=(16, 6), default=0.0)
    total_volume = fields.Float(string="总体积", digits=(16, 6), default=0.0)
    line_remark = fields.Text(string="行备注")

    goods_code = fields.Char(string="货物编码")
    goods_name = fields.Char(string="货物名称", required=True)
    specification = fields.Char(string="规格")
    quantity = fields.Float(string="数量", required=True, default=1.0)
    package_count = fields.Integer(string="件数", default=0)
    uom_name = fields.Char(string="单位")
    weight = fields.Float(string="重量")
    volume = fields.Float(string="体积")
    temperature_zone = fields.Selection(
        [("ambient", "常温"), ("chilled", "冷藏"), ("frozen", "冷冻"), ("other", "其他")],
        string="温层",
        default="ambient",
    )
    package_type = fields.Char(string="包装类型")
    remark = fields.Text(string="货物备注")

    @api.depends("customer_line_id.waybill_id.name")
    def _compute_waybill_no(self):
        for record in self:
            record.waybill_no = record.customer_line_id.waybill_id.name or ""

    @api.depends("customer_line_id.partner_no")
    def _compute_customer_no(self):
        for record in self:
            record.customer_no = record.customer_line_id.partner_no or ""

    @api.depends("customer_line_id.partner_name")
    def _compute_customer_name(self):
        for record in self:
            record.customer_name = record.customer_line_id.partner_name or ""

    @api.depends("customer_line_id.partner_no", "customer_line_id.partner_name")
    def _compute_partner_fields(self):
        for record in self:
            record.partner_no = record.customer_line_id.partner_no or ""
            record.partner_name = record.customer_line_id.partner_name or ""

    def _inverse_waybill_no(self):
        self._sync_customer_line_from_business_keys()

    def _inverse_customer_no(self):
        self._sync_customer_line_from_business_keys()

    def _inverse_customer_name(self):
        self._sync_customer_line_from_business_keys()

    def _inverse_partner_no(self):
        self._sync_customer_line_from_business_keys()

    def _inverse_partner_name(self):
        self._sync_customer_line_from_business_keys()

    def _sync_customer_line_from_business_keys(self):
        for record in self:
            waybill_no = (record.waybill_no or "").strip()
            customer_no = (record.customer_no or "").strip()
            customer_name = (record.customer_name or "").strip()
            if not waybill_no or (not customer_no and not customer_name):
                continue
            record.customer_line_id = self._resolve_customer_line(
                waybill_no,
                customer_no=customer_no,
                customer_name=customer_name,
            )

    @api.model
    def _ensure_unique_record(self, records, field_label, value):
        if not records:
            raise ValidationError(f"未找到“{field_label}” = {value} 对应的记录。")
        if len(records) > 1:
            raise ValidationError(f"“{field_label}” = {value} 匹配到多条记录，请先去重。")
        return records

    @api.model
    def _resolve_customer_line(self, waybill_no, *, customer_no=None, customer_name=None):
        customer_line_model = self.env["logistics.dispatch.waybill.customer.line"]
        domain = [("waybill_id.name", "=", waybill_no)]
        if customer_no:
            partner = customer_line_model._resolve_partner_by_code(customer_no)
            domain.append(("partner_id", "=", partner.id))
            label = "运单号 + 客户号"
            value = f"{waybill_no} / {customer_no}"
        elif customer_name:
            partner = customer_line_model._resolve_partner_by_name(customer_name)
            domain.append(("partner_id", "=", partner.id))
            label = "运单号 + 客户名称"
            value = f"{waybill_no} / {customer_name}"
        else:
            raise ValidationError("货物导入至少需要提供运单号与客户号或客户名称。")
        customer_lines = customer_line_model.search(domain, limit=2)
        return self._ensure_unique_record(customer_lines, label, value)

    @api.model_create_multi
    def create(self, vals_list):
        normalized_vals_list = []
        for vals in vals_list:
            normalized_vals = dict(vals)
            if "customer_line_id" not in normalized_vals:
                waybill_no = (normalized_vals.pop("waybill_no", "") or "").strip()
                customer_no = (normalized_vals.pop("customer_no", "") or "").strip()
                customer_name = (normalized_vals.pop("customer_name", "") or "").strip()
                if waybill_no and (customer_no or customer_name):
                    normalized_vals["customer_line_id"] = self._resolve_customer_line(
                        waybill_no,
                        customer_no=customer_no,
                        customer_name=customer_name,
                    ).id
            normalized_vals.setdefault("product_name_snapshot", normalized_vals.get("goods_name"))
            normalized_vals_list.append(normalized_vals)
        return super().create(normalized_vals_list)

    def write(self, vals):
        normalized_vals = dict(vals)
        if "customer_line_id" not in normalized_vals:
            waybill_no = (normalized_vals.pop("waybill_no", "") or "").strip()
            customer_no = (normalized_vals.pop("customer_no", "") or "").strip()
            customer_name = (normalized_vals.pop("customer_name", "") or "").strip()
            if waybill_no and (customer_no or customer_name):
                normalized_vals["customer_line_id"] = self._resolve_customer_line(
                    waybill_no,
                    customer_no=customer_no,
                    customer_name=customer_name,
                ).id
        return super().write(normalized_vals)

    @api.constrains("customer_line_id", "order_line_id")
    def _check_order_line_consistency(self):
        for record in self:
            if not record.order_line_id:
                continue
            if record.order_line_id.waybill_id != record.customer_line_id.waybill_id:
                raise ValidationError("Goods line order_line and customer_line must belong to the same waybill.")
            if record.order_line_id.customer_line_id and record.order_line_id.customer_line_id != record.customer_line_id:
                raise ValidationError("Goods line order_line and customer_line must point to the same customer node.")

    @api.constrains(
        "quantity",
        "package_count",
        "weight",
        "volume",
        "base_qty",
        "doc_qty",
        "small_qty",
        "box_qty",
        "gift_qty",
        "exchange_qty",
        "unit_weight",
        "unit_volume",
        "total_weight",
        "total_volume",
        "unit_price",
        "small_unit_price",
        "amount",
        "settled_amount",
        "unsettled_amount",
        "tax_amount",
        "amount_ex_tax",
        "cost_amount",
        "gross_profit",
    )
    def _check_non_negative_values(self):
        numeric_fields = (
            "package_count",
            "weight",
            "volume",
            "base_qty",
            "doc_qty",
            "small_qty",
            "box_qty",
            "gift_qty",
            "exchange_qty",
            "unit_weight",
            "unit_volume",
            "total_weight",
            "total_volume",
            "unit_price",
            "small_unit_price",
            "amount",
            "settled_amount",
            "unsettled_amount",
            "tax_amount",
            "amount_ex_tax",
            "cost_amount",
            "gross_profit",
        )
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("货物数量必须大于 0。")
            for field_name in numeric_fields:
                if record[field_name] < 0:
                    raise ValidationError(f"{record._fields[field_name].string} 不能小于 0。")
