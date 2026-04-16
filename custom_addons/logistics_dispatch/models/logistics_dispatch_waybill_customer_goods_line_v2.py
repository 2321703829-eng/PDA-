from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchWaybillCustomerGoodsLine(models.Model):
    _name = "logistics.dispatch.waybill.customer.goods.line"
    _description = "Waybill Customer Goods Line"
    _order = "sequence, id"

    @api.model
    def get_import_templates(self):
        return [
            {
                "label": self.env._("下载货物明细模板"),
                "template": "/logistics_dispatch/static/src/import_templates/运单货物明细导入模板.csv",
            }
        ]

    sequence = fields.Integer(string="Sequence", default=10)
    customer_line_id = fields.Many2one(
        "logistics.dispatch.waybill.customer.line",
        string="Customer Line",
        required=True,
        ondelete="cascade",
        index=True,
    )
    waybill_no = fields.Char(
        string="Waybill No (Import/Export)",
        compute="_compute_waybill_no",
        inverse="_inverse_waybill_no",
    )
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="Waybill",
        related="customer_line_id.waybill_id",
        store=True,
        readonly=True,
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        related="customer_line_id.customer_id",
        store=True,
        readonly=True,
    )
    customer_no = fields.Char(
        string="Customer No",
        compute="_compute_customer_no",
        inverse="_inverse_customer_no",
    )
    customer_name = fields.Char(
        string="Customer Name",
        compute="_compute_customer_name",
        inverse="_inverse_customer_name",
    )
    goods_code = fields.Char(string="Goods Code")
    goods_name = fields.Char(string="Goods Name", required=True)
    specification = fields.Char(string="Specification")
    quantity = fields.Float(string="Quantity", required=True, default=1.0)
    package_count = fields.Integer(string="Package Count", default=0)
    uom_name = fields.Char(string="UOM")
    weight = fields.Float(string="Weight")
    volume = fields.Float(string="Volume")
    temperature_zone = fields.Selection(
        [
            ("ambient", "Ambient"),
            ("chilled", "Chilled"),
            ("frozen", "Frozen"),
            ("other", "Other"),
        ],
        string="Temperature Zone",
        default="ambient",
    )
    package_type = fields.Char(string="Package Type")
    remark = fields.Text(string="Remark")

    @api.depends("customer_line_id.waybill_id.name")
    def _compute_waybill_no(self):
        for record in self:
            record.waybill_no = record.customer_line_id.waybill_id.name or ""

    @api.depends("customer_line_id.customer_id.logistics_customer_code")
    def _compute_customer_no(self):
        for record in self:
            record.customer_no = record.customer_line_id.customer_id.logistics_customer_code or ""

    @api.depends("customer_line_id.customer_id.name")
    def _compute_customer_name(self):
        for record in self:
            record.customer_name = record.customer_line_id.customer_id.name or ""

    def _inverse_waybill_no(self):
        self._sync_customer_line_from_business_keys()

    def _inverse_customer_no(self):
        self._sync_customer_line_from_business_keys()

    def _inverse_customer_name(self):
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
            raise ValidationError(f'No record found for "{field_label}" = {value}.')
        if len(records) > 1:
            raise ValidationError(f'"{field_label}" = {value} matched multiple records. Please deduplicate first.')
        return records

    @api.model
    def _resolve_customer_line(self, waybill_no, *, customer_no=None, customer_name=None):
        domain = [("waybill_id.name", "=", waybill_no)]
        if customer_no:
            domain.append(("customer_id.logistics_customer_code", "=", customer_no))
            label = "Waybill No + Customer No"
            value = f"{waybill_no} / {customer_no}"
        elif customer_name:
            domain.append(("customer_id.name", "=", customer_name))
            label = "Waybill No + Customer Name"
            value = f"{waybill_no} / {customer_name}"
        else:
            raise ValidationError("Goods import requires at least waybill_no and customer_no or customer_name.")
        customer_lines = self.env["logistics.dispatch.waybill.customer.line"].search(domain, limit=2)
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

    @api.constrains("quantity", "package_count", "weight", "volume")
    def _check_non_negative_values(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("Quantity must be greater than 0.")
            if record.package_count < 0:
                raise ValidationError("Package count cannot be less than 0.")
            if record.weight < 0 or record.volume < 0:
                raise ValidationError("Weight and volume cannot be negative.")
