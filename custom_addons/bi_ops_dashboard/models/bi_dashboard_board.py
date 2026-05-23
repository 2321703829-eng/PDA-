from odoo import _, fields, models


class BiOpsDashboardBoard(models.TransientModel):
    _name = "bi.ops.dashboard.board"
    _description = "BI Ops Dashboard Board"

    snapshot_date = fields.Date(string="Snapshot Date", required=True, default=lambda self: fields.Date.context_today(self))
    order_count = fields.Integer(string="Order Count", readonly=True)
    warehouse_task_count = fields.Integer(string="Warehouse Task Count", readonly=True)
    dispatch_count = fields.Integer(string="Dispatch Count", readonly=True)
    signoff_count = fields.Integer(string="Signoff Count", readonly=True)
    exception_count = fields.Integer(string="Exception Count", readonly=True)
    receipt_count = fields.Integer(string="Receipt Count", readonly=True)
    outbound_count = fields.Integer(string="Outbound Count", readonly=True)
    handover_count = fields.Integer(string="Handover Count", readonly=True)
    driver_task_count = fields.Integer(string="Driver Task Count", readonly=True)
    in_transit_count = fields.Integer(string="In Transit Count", readonly=True)
    signed_count = fields.Integer(string="Signed Count", readonly=True)
    revenue_amount = fields.Float(string="Revenue Amount", readonly=True, digits=(16, 2))
    cost_amount = fields.Float(string="Cost Amount", readonly=True, digits=(16, 2))
    freight_amount = fields.Float(string="Freight Amount", readonly=True, digits=(16, 2))
    gross_profit_amount = fields.Float(string="Gross Profit Amount", readonly=True, digits=(16, 2))

    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        return values

    def _load_snapshot_metrics(self):
        self.ensure_one()
        snapshot_date = self.snapshot_date or fields.Date.context_today(self)
        kpi = self.env["bi.daily.kpi.snapshot"].generate_snapshot(snapshot_date=snapshot_date)
        warehouse = self.env["bi.warehouse.dashboard.snapshot"].generate_snapshot(snapshot_date=snapshot_date)
        dispatch = self.env["bi.dispatch.dashboard.snapshot"].generate_snapshot(snapshot_date=snapshot_date)
        cost = self.env["bi.cost.profit.snapshot"].generate_snapshot(snapshot_date=snapshot_date)
        self.update(
            {
                "snapshot_date": snapshot_date,
                "order_count": kpi.order_count,
                "warehouse_task_count": kpi.warehouse_task_count,
                "dispatch_count": kpi.dispatch_count,
                "signoff_count": kpi.signoff_count,
                "exception_count": kpi.exception_count,
                "receipt_count": warehouse.receipt_count,
                "outbound_count": warehouse.outbound_count,
                "handover_count": warehouse.handover_count,
                "driver_task_count": dispatch.driver_task_count,
                "in_transit_count": dispatch.in_transit_count,
                "signed_count": dispatch.signed_count,
                "revenue_amount": cost.revenue_amount,
                "cost_amount": cost.cost_amount,
                "freight_amount": cost.freight_amount,
                "gross_profit_amount": cost.gross_profit_amount,
            }
        )

    def action_refresh_board(self):
        self.ensure_one()
        self._load_snapshot_metrics()
        if "core.operation.audit.log" in self.env.registry:
            self.env["core.operation.audit.log"].log_action(
                business_domain="bi",
                action_code="bi_open_ops_dashboard_board",
                note=_("BI operations dashboard board refreshed."),
                payload={"snapshot_date": str(self.snapshot_date)},
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("BI Ops Dashboard"),
            "res_model": "bi.ops.dashboard.board",
            "view_mode": "form",
            "res_id": self.id,
            "target": "current",
        }

    def _open_snapshot_action(self, xmlid, snapshot_model):
        self.ensure_one()
        snapshot = self.env[snapshot_model].generate_snapshot(snapshot_date=self.snapshot_date)
        action = self.env.ref(xmlid).read()[0]
        action["domain"] = [("snapshot_date", "=", self.snapshot_date)]
        action["context"] = {"default_snapshot_date": self.snapshot_date}
        if len(snapshot) == 1:
            action["views"] = [(False, "form"), (False, "list")]
            action["res_id"] = snapshot.id
        return action

    def action_open_kpi_report(self):
        return self._open_snapshot_action("bi_ops_dashboard.action_bi_daily_kpi_snapshot", "bi.daily.kpi.snapshot")

    def action_open_order_dashboard(self):
        return self._open_snapshot_action("bi_ops_dashboard.action_bi_order_dashboard_snapshot", "bi.order.dashboard.snapshot")

    def action_open_warehouse_dashboard(self):
        return self._open_snapshot_action("bi_ops_dashboard.action_bi_warehouse_dashboard_snapshot", "bi.warehouse.dashboard.snapshot")

    def action_open_dispatch_dashboard(self):
        return self._open_snapshot_action("bi_ops_dashboard.action_bi_dispatch_dashboard_snapshot", "bi.dispatch.dashboard.snapshot")

    def action_open_exception_ledger(self):
        return self._open_snapshot_action("bi_ops_dashboard.action_bi_exception_snapshot", "bi.exception.snapshot")

    def action_open_cost_dashboard(self):
        return self._open_snapshot_action("bi_ops_dashboard.action_bi_cost_profit_snapshot", "bi.cost.profit.snapshot")
