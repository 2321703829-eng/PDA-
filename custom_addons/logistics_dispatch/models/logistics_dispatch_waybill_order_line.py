from odoo import api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.logistics_dispatch.models.selection_options import (
    AUDIT_STATUS_SELECTION,
    DOC_STATUS_SELECTION,
    LOGISTICS_STATUS_SELECTION,
    PAYMENT_STATUS_SELECTION,
    SETTLEMENT_STATUS_SELECTION,
)


class LogisticsDispatchWaybillOrderLine(models.Model):
    _name = "logistics.dispatch.waybill.order.line"
    _description = "运单订单明细"
    _order = "id"

    _uniq_customer_line_source_doc_no = models.Constraint(
        "unique(customer_line_id, source_doc_no)",
        "同一配送节点下的来源单号必须唯一。",
    )

    waybill_id = fields.Many2one("logistics.dispatch.waybill", string="运单", required=True, ondelete="cascade", index=True)
    customer_line_id = fields.Many2one(
        "logistics.dispatch.waybill.customer.line",
        string="配送节点",
        ondelete="cascade",
        index=True,
    )
    sale_order_id = fields.Many2one("sale.order", string="销售订单", ondelete="set null")
    stock_picking_id = fields.Many2one("stock.picking", string="出库单", ondelete="set null")
    source_doc_no = fields.Char(string="来源单号", size=64, index=True)
    order_no = fields.Char(string="订单号", size=64, index=True)
    sales_order_no = fields.Char(string="销售单号", size=64, index=True)
    source_ref_no = fields.Char(string="来源引用号", size=64, index=True)
    third_party_doc_no = fields.Char(string="第三方单号", size=64, index=True)
    external_order_no = fields.Char(string="外部单号", size=64, index=True)
    doc_type = fields.Char(string="单据类型", size=32)
    business_type = fields.Char(string="业务类型", size=32)
    doc_source = fields.Char(string="单据来源", size=32)
    doc_date = fields.Date(string="单据日期", index=True)
    audited_at = fields.Date(string="审核日期")
    department_name_snapshot = fields.Char(string="部门快照", size=64)
    channel_name_snapshot = fields.Char(string="渠道快照", size=64)
    gathering_location = fields.Char(string="集货位", size=64)
    salesperson_phone = fields.Char(string="业务员联系方式", size=64)
    salesperson_name_snapshot = fields.Char(string="业务员快照", size=64)
    payment_status = fields.Selection(selection=PAYMENT_STATUS_SELECTION, string="支付状态", index=True)
    audit_status = fields.Selection(selection=AUDIT_STATUS_SELECTION, string="审核状态", index=True)
    settlement_status = fields.Selection(selection=SETTLEMENT_STATUS_SELECTION, string="结算状态", index=True)
    doc_status = fields.Selection(selection=DOC_STATUS_SELECTION, string="单据状态", index=True)
    logistics_status = fields.Selection(selection=LOGISTICS_STATUS_SELECTION, string="物流状态", index=True)
    whole_package_count = fields.Float(string="整件数", digits=(16, 4), default=0.0)
    loose_package_count = fields.Float(string="散件数", digits=(16, 4), default=0.0)
    maker_name = fields.Char(string="制单人", size=64)
    auditor_name = fields.Char(string="审核人", size=64)
    made_at = fields.Datetime(string="制单时间")
    order_remark = fields.Text(string="备注")
    custom_field_1 = fields.Char(string="扩展字段1", size=128)

    store_id = fields.Many2one("res.partner", string="客户", domain="[('is_logistics_partner', '=', True)]")
    goods_summary = fields.Char(string="货物摘要")
    qty_summary = fields.Float(string="数量", digits=(16, 4), default=0.0)
    weight_summary = fields.Float(string="重量", digits=(16, 6), default=0.0)
    volume_summary = fields.Float(string="体积", digits=(16, 6), default=0.0)
    line_state = fields.Selection(
        [("draft", "草稿"), ("ready", "待执行"), ("done", "已完成"), ("cancelled", "已取消")],
        string="明细状态",
        default="draft",
        required=True,
    )
    goods_line_ids = fields.One2many("logistics.dispatch.waybill.customer.goods.line", "order_line_id", string="货物明细")

    batch_id = fields.Many2one(
        "logistics.dispatch.batch",
        string="批次",
        related="waybill_id.batch_id",
        store=True,
        readonly=True,
        index=True,
    )
    batch_no = fields.Char(
        string="批次号",
        related="waybill_id.batch_no",
        store=True,
        readonly=True,
        index=True,
    )
    customer_line_no = fields.Char(
        string="配送节点编号",
        related="customer_line_id.customer_line_no",
        store=True,
        readonly=True,
    )

    @api.constrains("whole_package_count", "loose_package_count")
    def _check_non_negative_summary_values(self):
        for record in self:
            if record.whole_package_count < 0 or record.loose_package_count < 0:
                raise ValidationError("整件数和散件数不能小于 0。")

    @api.constrains(
        "source_doc_no",
        "order_no",
        "sales_order_no",
        "source_ref_no",
        "third_party_doc_no",
        "external_order_no",
    )
    def _check_business_key_presence(self):
        key_fields = (
            "source_doc_no",
            "order_no",
            "sales_order_no",
            "source_ref_no",
            "third_party_doc_no",
            "external_order_no",
        )
        for record in self:
            if not any(record[field_name] for field_name in key_fields):
                raise ValidationError("订单明细至少需要保留一个业务键字段。")

    @api.constrains("waybill_id", "customer_line_id")
    def _check_customer_line_belongs_to_waybill(self):
        for record in self:
            if record.customer_line_id and record.customer_line_id.waybill_id != record.waybill_id:
                raise ValidationError("Order line customer_line must belong to the same waybill.")

    @api.model
    def _build_snapshot_vals(self, normalized_vals):
        customer_line = (
            self.env["logistics.dispatch.waybill.customer.line"].browse(normalized_vals["customer_line_id"])
            if normalized_vals.get("customer_line_id")
            else False
        )
        partner = customer_line.partner_id if customer_line else False
        return {
            "waybill_id": customer_line.waybill_id.id if customer_line and not normalized_vals.get("waybill_id") else normalized_vals.get("waybill_id"),
            "store_id": partner.id if partner and not normalized_vals.get("store_id") else normalized_vals.get("store_id"),
            "department_name_snapshot": partner.department_name or False,
            "channel_name_snapshot": partner.channel_name or False,
            "salesperson_name_snapshot": partner.salesperson_name or False,
        }

    @api.model_create_multi
    def create(self, vals_list):
        normalized_vals_list = []
        for vals in vals_list:
            normalized_vals = dict(vals)
            if normalized_vals.get("customer_line_id"):
                for field_name, field_value in self._build_snapshot_vals(normalized_vals).items():
                    normalized_vals.setdefault(field_name, field_value)
            normalized_vals_list.append(normalized_vals)
        return super().create(normalized_vals_list)

    def write(self, vals):
        normalized_vals = dict(vals)
        if normalized_vals.get("customer_line_id"):
            for field_name, field_value in self._build_snapshot_vals(normalized_vals).items():
                normalized_vals.setdefault(field_name, field_value)
        return super().write(normalized_vals)

    @api.onchange("customer_line_id")
    def _onchange_customer_line_id(self):
        for record in self:
            if record.customer_line_id:
                record.waybill_id = record.customer_line_id.waybill_id
                record.store_id = record.customer_line_id.partner_id
