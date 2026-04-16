from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchWaybillImportSupport(models.Model):
    _inherit = "logistics.dispatch.waybill"

    @api.model
    def get_import_templates(self):
        return [
            {
                "label": self.env._("下载运单标准模板"),
                "template": "/logistics_dispatch/static/src/import_templates/logistics_dispatch_waybill_import_template.csv",
            },
            {
                "label": self.env._("下载客户明细模板"),
                "template": "/logistics_dispatch/static/src/import_templates/logistics_dispatch_waybill_customer_line_import_template.csv",
            },
            {
                "label": self.env._("下载货物明细模板"),
                "template": "/logistics_dispatch/static/src/import_templates/logistics_dispatch_waybill_customer_goods_line_import_template.csv",
            },
        ]


class LogisticsDispatchWaybillCustomerLineImportSupport(models.Model):
    _inherit = "logistics.dispatch.waybill.customer.line"

    @api.model
    def get_import_templates(self):
        return [
            {
                "label": self.env._("下载客户明细模板"),
                "template": "/logistics_dispatch/static/src/import_templates/logistics_dispatch_waybill_customer_line_import_template.csv",
            },
            {
                "label": self.env._("下载货物明细模板"),
                "template": "/logistics_dispatch/static/src/import_templates/logistics_dispatch_waybill_customer_goods_line_import_template.csv",
            },
        ]

    @api.model
    def _resolve_waybill_by_no(self, waybill_no):
        waybills = self.env["logistics.dispatch.waybill"].search([("name", "=", waybill_no)], limit=2)
        return self._ensure_unique_record(waybills, "运单号", waybill_no)

    @api.model_create_multi
    def create(self, vals_list):
        normalized_vals_list = []
        for vals in vals_list:
            normalized_vals = dict(vals)
            if "waybill_no" in normalized_vals and "waybill_id" not in normalized_vals:
                waybill_no = (normalized_vals.pop("waybill_no") or "").strip()
                normalized_vals["waybill_id"] = self._resolve_waybill_by_no(waybill_no).id if waybill_no else False
            normalized_vals_list.append(normalized_vals)
        return super().create(normalized_vals_list)

    def write(self, vals):
        normalized_vals = dict(vals)
        if "waybill_no" in normalized_vals and "waybill_id" not in normalized_vals:
            waybill_no = (normalized_vals.pop("waybill_no") or "").strip()
            normalized_vals["waybill_id"] = self._resolve_waybill_by_no(waybill_no).id if waybill_no else False
        return super().write(normalized_vals)


class LogisticsDispatchWaybillCustomerGoodsLineImportSupport(models.Model):
    _inherit = "logistics.dispatch.waybill.customer.goods.line"

    waybill_no = fields.Char(
        string="运单号（导入导出）",
        compute="_compute_waybill_no",
        inverse="_inverse_waybill_no",
    )
    customer_no = fields.Char(
        string="客户编号",
        compute="_compute_customer_no",
        inverse="_inverse_customer_no",
    )
    customer_name = fields.Char(
        string="客户名称",
        compute="_compute_customer_name",
        inverse="_inverse_customer_name",
    )

    @api.model
    def get_import_templates(self):
        return [
            {
                "label": self.env._("下载货物明细模板"),
                "template": "/logistics_dispatch/static/src/import_templates/logistics_dispatch_waybill_customer_goods_line_import_template.csv",
            }
        ]

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
    def _ensure_unique_import_record(self, records, field_label, value):
        if not records:
            raise ValidationError(f"未找到“{field_label}”={value} 对应的记录。")
        if len(records) > 1:
            raise ValidationError(f"“{field_label}”={value} 匹配到多条记录，请先去重。")
        return records

    @api.model
    def _resolve_customer_line(self, waybill_no, *, customer_no=None, customer_name=None):
        domain = [("waybill_id.name", "=", waybill_no)]
        if customer_no:
            domain.append(("customer_id.logistics_customer_code", "=", customer_no))
            label = "运单号 + 客户编号"
            value = f"{waybill_no} / {customer_no}"
        elif customer_name:
            domain.append(("customer_id.name", "=", customer_name))
            label = "运单号 + 客户名称"
            value = f"{waybill_no} / {customer_name}"
        else:
            raise ValidationError("货物导入必须至少提供运单号和客户编号或客户名称。")
        customer_lines = self.env["logistics.dispatch.waybill.customer.line"].search(domain, limit=2)
        return self._ensure_unique_import_record(customer_lines, label, value)

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
