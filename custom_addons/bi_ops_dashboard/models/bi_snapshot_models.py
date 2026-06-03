from datetime import datetime, time

from odoo import _, api, fields, models


class BiSnapshotMixin(models.AbstractModel):
    _name = "bi.snapshot.mixin"
    _description = "BI Snapshot Mixin"

    @api.model
    def _day_range(self, snapshot_date):
        start = datetime.combine(fields.Date.to_date(snapshot_date), time.min)
        end = datetime.combine(fields.Date.to_date(snapshot_date), time.max)
        return fields.Datetime.to_string(start), fields.Datetime.to_string(end)

    def _log_audit(self, action_code, record=None, note="", payload=None):
        if "core.operation.audit.log" in self.env.registry:
            self.env["core.operation.audit.log"].log_action(
                business_domain="bi",
                action_code=action_code,
                record=record or self,
                note=note,
                payload=payload or {},
            )


class BiDailyKpiSnapshot(models.Model):
    _name = "bi.daily.kpi.snapshot"
    _description = "BI Daily KPI Snapshot"
    _inherit = "bi.snapshot.mixin"
    _order = "snapshot_date desc, id desc"

    snapshot_date = fields.Date(string="Snapshot Date", required=True, index=True)
    order_count = fields.Integer(string="Order Count", default=0)
    warehouse_task_count = fields.Integer(string="Warehouse Task Count", default=0)
    dispatch_count = fields.Integer(string="Dispatch Count", default=0)
    signoff_count = fields.Integer(string="Signoff Count", default=0)
    exception_count = fields.Integer(string="Exception Count", default=0)

    @api.model
    def generate_snapshot(self, snapshot_date=None):
        snapshot_date = snapshot_date or fields.Date.context_today(self)
        start_dt, end_dt = self._day_range(snapshot_date)
        values = {
            "snapshot_date": snapshot_date,
            "order_count": self.env["logistics.dispatch.waybill"].search_count([("delivery_date", "=", snapshot_date)]),
            "warehouse_task_count": sum(
                self.env[model].search_count([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)])
                for model in (
                    "wms.receipt.task",
                    "wms.putaway.task",
                    "wms.outbound.task",
                    "wms.pick.task",
                    "wms.check.task",
                    "wms.handover.order",
                )
            ),
            "dispatch_count": self.env["tms.dispatch.order"].search_count([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)]),
            "signoff_count": self.env["tms.signoff.receipt"].search_count([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)]),
            "exception_count": self.env["tms.delivery.exception"].search_count([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)]),
        }
        snapshot = self.search([("snapshot_date", "=", snapshot_date)], limit=1)
        if snapshot:
            snapshot.write(values)
        else:
            snapshot = self.create(values)
        return snapshot

    def action_generate_today_snapshot(self):
        snapshot = self.generate_snapshot()
        self._log_audit("bi_generate_daily_kpi_snapshot", record=snapshot,
                        note=_("Daily KPI snapshot generated."),
                        payload={"snapshot_date": str(snapshot.snapshot_date)})
        return snapshot.action_open_record()

    def action_generate_all_today_snapshots(self):
        self.ensure_one()
        snapshot_date = self.snapshot_date or fields.Date.context_today(self)
        self.generate_snapshot(snapshot_date=snapshot_date)
        self.env["bi.order.dashboard.snapshot"].generate_snapshot(snapshot_date=snapshot_date)
        self.env["bi.warehouse.dashboard.snapshot"].generate_snapshot(snapshot_date=snapshot_date)
        self.env["bi.dispatch.dashboard.snapshot"].generate_snapshot(snapshot_date=snapshot_date)
        self.env["bi.exception.snapshot"].generate_snapshot(snapshot_date=snapshot_date)
        self.env["bi.cost.profit.snapshot"].generate_snapshot(snapshot_date=snapshot_date)
        self._log_audit("bi_generate_all_snapshots",
                        note=_("All BI snapshots generated."),
                        payload={"snapshot_date": str(snapshot_date)})
        return self.action_open_record()

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Daily KPI Snapshot"),
            "res_model": "bi.daily.kpi.snapshot",
            "view_mode": "form",
            "res_id": self.id,
        }

    def action_open_order_details(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Waybills"),
            "res_model": "logistics.dispatch.waybill",
            "view_mode": "list,form",
            "domain": [("delivery_date", "=", self.snapshot_date)],
        }

    def action_open_exception_details(self):
        self.ensure_one()
        start_dt, end_dt = self._day_range(self.snapshot_date)
        return {
            "type": "ir.actions.act_window",
            "name": _("Delivery Exceptions"),
            "res_model": "tms.delivery.exception",
            "view_mode": "list,form",
            "domain": [("create_date", ">=", start_dt), ("create_date", "<=", end_dt)],
        }

    def action_open_warehouse_snapshot(self):
        self.ensure_one()
        snapshot = self.env["bi.warehouse.dashboard.snapshot"].generate_snapshot(snapshot_date=self.snapshot_date)
        return snapshot.action_open_record()

    def action_open_dispatch_snapshot(self):
        self.ensure_one()
        snapshot = self.env["bi.dispatch.dashboard.snapshot"].generate_snapshot(snapshot_date=self.snapshot_date)
        return snapshot.action_open_record()

    def action_open_cost_snapshot(self):
        self.ensure_one()
        snapshot = self.env["bi.cost.profit.snapshot"].generate_snapshot(snapshot_date=self.snapshot_date)
        return snapshot.action_open_record()


class BiExceptionSnapshot(models.Model):
    _name = "bi.exception.snapshot"
    _description = "BI Exception Snapshot"
    _inherit = "bi.snapshot.mixin"
    _order = "snapshot_date desc, id desc"

    snapshot_date = fields.Date(string="Snapshot Date", required=True, index=True)
    exception_type = fields.Char(string="Exception Type")
    exception_count = fields.Integer(string="Exception Count", default=0)
    open_count = fields.Integer(string="Open Count", default=0)
    closed_count = fields.Integer(string="Closed Count", default=0)

    @api.model
    def generate_snapshot(self, snapshot_date=None):
        snapshot_date = snapshot_date or fields.Date.context_today(self)
        start_dt, end_dt = self._day_range(snapshot_date)
        exception_model = self.env["tms.delivery.exception"]
        records = exception_model.search([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)])
        existing = self.search([("snapshot_date", "=", snapshot_date)])
        if existing:
            existing.unlink()
        result = self.browse()
        for exception_type in sorted(set(records.mapped("exception_type"))):
            subset = records.filtered(lambda rec: rec.exception_type == exception_type)
            result |= self.create({
                "snapshot_date": snapshot_date,
                "exception_type": exception_type,
                "exception_count": len(subset),
                "open_count": len(subset.filtered(lambda rec: rec.state == "delivery_exception")),
                "closed_count": 0,
            })
        return result

    def action_generate_today_snapshot(self):
        snapshots = self.generate_snapshot()
        if snapshots:
            self._log_audit("bi_generate_exception_snapshot", record=snapshots[0],
                            note=_("Exception snapshots generated."),
                            payload={"snapshot_date": str(snapshots[0].snapshot_date), "row_count": len(snapshots)})
        action = self.env.ref("bi_ops_dashboard.action_bi_exception_snapshot").read()[0]
        action["domain"] = [("id", "in", snapshots.ids)]
        return action

    def action_open_exception_details(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Delivery Exceptions"),
            "res_model": "tms.delivery.exception",
            "view_mode": "list,form",
            "domain": [("exception_type", "=", self.exception_type)],
        }

    def action_open_snapshot_day(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Exception Snapshots"),
            "res_model": "bi.exception.snapshot",
            "view_mode": "list,form",
            "domain": [("snapshot_date", "=", self.snapshot_date)],
        }


class BiOrderDashboardSnapshot(models.Model):
    _name = "bi.order.dashboard.snapshot"
    _description = "BI Order Dashboard Snapshot"
    _inherit = "bi.snapshot.mixin"
    _order = "snapshot_date desc, id desc"

    snapshot_date = fields.Date(string="Snapshot Date", required=True, index=True)
    waybill_count = fields.Integer(string="Waybill Count", default=0)
    customer_line_count = fields.Integer(string="Customer Line Count", default=0)
    goods_line_count = fields.Integer(string="Goods Line Count", default=0)
    order_line_count = fields.Integer(string="Order Line Count", default=0)

    @api.model
    def generate_snapshot(self, snapshot_date=None):
        snapshot_date = snapshot_date or fields.Date.context_today(self)
        waybills = self.env["logistics.dispatch.waybill"].search([("delivery_date", "=", snapshot_date)])
        values = {
            "snapshot_date": snapshot_date,
            "waybill_count": len(waybills),
            "customer_line_count": sum(waybills.mapped("customer_line_count")),
            "goods_line_count": sum(waybills.mapped("goods_line_count")),
            "order_line_count": sum(waybills.mapped("order_line_count")),
        }
        snapshot = self.search([("snapshot_date", "=", snapshot_date)], limit=1)
        if snapshot:
            snapshot.write(values)
        else:
            snapshot = self.create(values)
        return snapshot

    def action_generate_today_snapshot(self):
        snapshot = self.generate_snapshot()
        self._log_audit("bi_generate_order_dashboard_snapshot", record=snapshot,
                        note=_("Order dashboard snapshot generated."),
                        payload={"snapshot_date": str(snapshot.snapshot_date)})
        return snapshot.action_open_record()

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Order Dashboard Snapshot"),
            "res_model": "bi.order.dashboard.snapshot",
            "view_mode": "form",
            "res_id": self.id,
        }

    def action_open_waybills(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Waybills"),
            "res_model": "logistics.dispatch.waybill",
            "view_mode": "list,form",
            "domain": [("delivery_date", "=", self.snapshot_date)],
        }


class BiWarehouseDashboardSnapshot(models.Model):
    _name = "bi.warehouse.dashboard.snapshot"
    _description = "BI Warehouse Dashboard Snapshot"
    _inherit = "bi.snapshot.mixin"
    _order = "snapshot_date desc, id desc"

    snapshot_date = fields.Date(string="Snapshot Date", required=True, index=True)
    receipt_count = fields.Integer(string="Receipt Count", default=0)
    putaway_count = fields.Integer(string="Putaway Count", default=0)
    outbound_count = fields.Integer(string="Outbound Count", default=0)
    pick_count = fields.Integer(string="Pick Count", default=0)
    check_count = fields.Integer(string="Check Count", default=0)
    handover_count = fields.Integer(string="Handover Count", default=0)

    @api.model
    def generate_snapshot(self, snapshot_date=None):
        snapshot_date = snapshot_date or fields.Date.context_today(self)
        start_dt, end_dt = self._day_range(snapshot_date)
        values = {
            "snapshot_date": snapshot_date,
            "receipt_count": self.env["wms.receipt.task"].search_count([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)]),
            "putaway_count": self.env["wms.putaway.task"].search_count([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)]),
            "outbound_count": self.env["wms.outbound.task"].search_count([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)]),
            "pick_count": self.env["wms.pick.task"].search_count([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)]),
            "check_count": self.env["wms.check.task"].search_count([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)]),
            "handover_count": self.env["wms.handover.order"].search_count([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)]),
        }
        snapshot = self.search([("snapshot_date", "=", snapshot_date)], limit=1)
        if snapshot:
            snapshot.write(values)
        else:
            snapshot = self.create(values)
        return snapshot

    def action_generate_today_snapshot(self):
        snapshot = self.generate_snapshot()
        self._log_audit("bi_generate_warehouse_dashboard_snapshot", record=snapshot,
                        note=_("Warehouse dashboard snapshot generated."),
                        payload={"snapshot_date": str(snapshot.snapshot_date)})
        return snapshot.action_open_record()

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Warehouse Dashboard Snapshot"),
            "res_model": "bi.warehouse.dashboard.snapshot",
            "view_mode": "form",
            "res_id": self.id,
        }

    def action_open_outbound_tasks(self):
        self.ensure_one()
        start_dt, end_dt = self._day_range(self.snapshot_date)
        return {
            "type": "ir.actions.act_window",
            "name": _("Outbound Tasks"),
            "res_model": "wms.outbound.task",
            "view_mode": "list,form",
            "domain": [("create_date", ">=", start_dt), ("create_date", "<=", end_dt)],
        }

    def action_open_receipt_tasks(self):
        self.ensure_one()
        start_dt, end_dt = self._day_range(self.snapshot_date)
        return {
            "type": "ir.actions.act_window",
            "name": _("Receipt Tasks"),
            "res_model": "wms.receipt.task",
            "view_mode": "list,form",
            "domain": [("create_date", ">=", start_dt), ("create_date", "<=", end_dt)],
        }

    def action_open_inventory_operations(self):
        self.ensure_one()
        start_dt, end_dt = self._day_range(self.snapshot_date)
        return {
            "type": "ir.actions.act_window",
            "name": _("Inventory Operations"),
            "res_model": "wms.inventory.operation",
            "view_mode": "list,form",
            "domain": [("create_date", ">=", start_dt), ("create_date", "<=", end_dt)],
        }


class BiDispatchDashboardSnapshot(models.Model):
    _name = "bi.dispatch.dashboard.snapshot"
    _description = "BI Dispatch Dashboard Snapshot"
    _inherit = "bi.snapshot.mixin"
    _order = "snapshot_date desc, id desc"

    snapshot_date = fields.Date(string="Snapshot Date", required=True, index=True)
    dispatch_count = fields.Integer(string="Dispatch Count", default=0)
    driver_task_count = fields.Integer(string="Driver Task Count", default=0)
    in_transit_count = fields.Integer(string="In Transit Count", default=0)
    signed_count = fields.Integer(string="Signed Count", default=0)
    exception_count = fields.Integer(string="Exception Count", default=0)

    @api.model
    def generate_snapshot(self, snapshot_date=None):
        snapshot_date = snapshot_date or fields.Date.context_today(self)
        start_dt, end_dt = self._day_range(snapshot_date)
        driver_tasks = self.env["tms.driver.task"].search([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)])
        values = {
            "snapshot_date": snapshot_date,
            "dispatch_count": self.env["tms.dispatch.order"].search_count([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)]),
            "driver_task_count": len(driver_tasks),
            "in_transit_count": len(driver_tasks.filtered(lambda rec: rec.state in ("departed", "in_transit", "arrived_store"))),
            "signed_count": len(driver_tasks.filtered(lambda rec: rec.state in ("signed_full", "signed_partial"))),
            "exception_count": len(driver_tasks.filtered(lambda rec: rec.state == "delivery_exception")),
        }
        snapshot = self.search([("snapshot_date", "=", snapshot_date)], limit=1)
        if snapshot:
            snapshot.write(values)
        else:
            snapshot = self.create(values)
        return snapshot

    def action_generate_today_snapshot(self):
        snapshot = self.generate_snapshot()
        self._log_audit("bi_generate_dispatch_dashboard_snapshot", record=snapshot,
                        note=_("Dispatch dashboard snapshot generated."),
                        payload={"snapshot_date": str(snapshot.snapshot_date)})
        return snapshot.action_open_record()

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Dispatch Dashboard Snapshot"),
            "res_model": "bi.dispatch.dashboard.snapshot",
            "view_mode": "form",
            "res_id": self.id,
        }

    def action_open_driver_tasks(self):
        self.ensure_one()
        start_dt, end_dt = self._day_range(self.snapshot_date)
        return {
            "type": "ir.actions.act_window",
            "name": _("Driver Tasks"),
            "res_model": "tms.driver.task",
            "view_mode": "list,form",
            "domain": [("create_date", ">=", start_dt), ("create_date", "<=", end_dt)],
        }

    def action_open_dispatch_orders(self):
        self.ensure_one()
        start_dt, end_dt = self._day_range(self.snapshot_date)
        return {
            "type": "ir.actions.act_window",
            "name": _("Dispatch Orders"),
            "res_model": "tms.dispatch.order",
            "view_mode": "list,form",
            "domain": [("create_date", ">=", start_dt), ("create_date", "<=", end_dt)],
        }

    def action_open_delivery_exceptions(self):
        self.ensure_one()
        start_dt, end_dt = self._day_range(self.snapshot_date)
        return {
            "type": "ir.actions.act_window",
            "name": _("Delivery Exceptions"),
            "res_model": "tms.delivery.exception",
            "view_mode": "list,form",
            "domain": [("create_date", ">=", start_dt), ("create_date", "<=", end_dt)],
        }


class BiCostProfitSnapshot(models.Model):
    _name = "bi.cost.profit.snapshot"
    _description = "BI Cost Profit Snapshot"
    _inherit = "bi.snapshot.mixin"
    _order = "snapshot_date desc, id desc"

    snapshot_date = fields.Date(string="Snapshot Date", required=True, index=True)
    revenue_amount = fields.Float(string="Revenue Amount", digits=(16, 2), default=0.0)
    cost_amount = fields.Float(string="Cost Amount", digits=(16, 2), default=0.0)
    freight_amount = fields.Float(string="Freight Amount", digits=(16, 2), default=0.0)
    gross_profit_amount = fields.Float(string="Gross Profit Amount", digits=(16, 2), default=0.0)

    @api.model
    def generate_snapshot(self, snapshot_date=None):
        snapshot_date = snapshot_date or fields.Date.context_today(self)
        start_dt, end_dt = self._day_range(snapshot_date)
        freight_lines = self.env["tms.freight.fee.line"].search([("create_date", ">=", start_dt), ("create_date", "<=", end_dt)])
        freight_amount = sum(freight_lines.mapped("amount"))
        values = {
            "snapshot_date": snapshot_date,
            "revenue_amount": 0.0,
            "cost_amount": freight_amount,
            "freight_amount": freight_amount,
            "gross_profit_amount": 0.0 - freight_amount,
        }
        snapshot = self.search([("snapshot_date", "=", snapshot_date)], limit=1)
        if snapshot:
            snapshot.write(values)
        else:
            snapshot = self.create(values)
        return snapshot

    def action_generate_today_snapshot(self):
        snapshot = self.generate_snapshot()
        self._log_audit("bi_generate_cost_profit_snapshot", record=snapshot,
                        note=_("Cost profit snapshot generated."),
                        payload={"snapshot_date": str(snapshot.snapshot_date)})
        return snapshot.action_open_record()

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Cost Profit Snapshot"),
            "res_model": "bi.cost.profit.snapshot",
            "view_mode": "form",
            "res_id": self.id,
        }

    def action_open_freight_lines(self):
        self.ensure_one()
        start_dt, end_dt = self._day_range(self.snapshot_date)
        return {
            "type": "ir.actions.act_window",
            "name": _("Freight Fee Lines"),
            "res_model": "tms.freight.fee.line",
            "view_mode": "list,form",
            "domain": [("create_date", ">=", start_dt), ("create_date", "<=", end_dt)],
        }
