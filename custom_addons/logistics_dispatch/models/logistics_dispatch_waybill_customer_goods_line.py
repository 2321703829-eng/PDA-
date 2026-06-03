from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchWaybillCustomerGoodsLine(models.Model):
    _name = "logistics.dispatch.waybill.customer.goods.line"
    _description = "运单客户货物明细"
    _order = "sequence, id"

    @api.model
    def get_import_templates(self):
        return [
            {
                "label": self.env._("下载货物明细模板"),
                "template": "/logistics_dispatch/static/src/import_templates/运单货物明细导入模板.csv",
            }
        ]

    sequence = fields.Integer(string="排序", default=10)
    customer_line_id = fields.Many2one(
        "logistics.dispatch.waybill.customer.line",
        string="客户明细",
        required=True,
        ondelete="cascade",
        index=True,
    )
    waybill_no = fields.Char(
        string="运单号（导入导出）",
        compute="_compute_waybill_no",
        inverse="_inverse_waybill_no",
    )
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
    customer_no = fields.Char(
        string="客户号",
        compute="_compute_customer_no",
        inverse="_inverse_customer_no",
    )
    customer_name = fields.Char(
        string="客户名称",
        compute="_compute_customer_name",
        inverse="_inverse_customer_name",
    )
    goods_code = fields.Char(string="货物编码")
    goods_name = fields.Char(string="货物名称", required=True)
    specification = fields.Char(string="规格")
    quantity = fields.Float(string="数量", required=True, default=1.0)
    package_count = fields.Integer(string="件数", default=0)
    uom_name = fields.Char(string="单位")
    weight = fields.Float(string="重量")
    volume = fields.Float(string="体积")
    temperature_zone = fields.Selection(
        [
            ("ambient", "常温"),
            ("chilled", "冷藏"),
            ("frozen", "冷冻"),
            ("other", "其他"),
        ],
        string="温层",
        default="ambient",
    )
    package_type = fields.Char(string="包装类型")
    remark = fields.Text(string="货物备注")

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
            raise ValidationError(f'未找到“{field_label}” = {value} 对应的记录。')
        if len(records) > 1:
            raise ValidationError(f'“{field_label}” = {value} 匹配到多条记录，请先去重。')
        return records

    @api.model
    def _resolve_customer_line(self, waybill_no, *, customer_no=None, customer_name=None):
        domain = [("waybill_id.name", "=", waybill_no)]
        if customer_no:
            domain.append(("customer_id.logistics_customer_code", "=", customer_no))
            label = "运单号 + 客户号"
            value = f"{waybill_no} / {customer_no}"
        elif customer_name:
            domain.append(("customer_id.name", "=", customer_name))
            label = "运单号 + 客户名称"
            value = f"{waybill_no} / {customer_name}"
        else:
            raise ValidationError("货物导入至少需要提供运单号与客户号或客户名称。")
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
                raise ValidationError("货物数量必须大于 0。")
            if record.package_count < 0:
                raise ValidationError("货物件数不能小于 0。")
            if record.weight < 0 or record.volume < 0:
                raise ValidationError("货物重量和体积不能为负数。")

    def action_logistics_delete(self):
        self.unlink()
        return True

    def action_logistics_archive(self):
        return self.action_logistics_delete()
