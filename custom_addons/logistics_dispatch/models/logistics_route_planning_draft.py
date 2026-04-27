from odoo import api, fields, models


class LogisticsRoutePlanningBatch(models.Model):
    _name = "logistics.route.planning.batch"
    _description = "排线批次草稿"
    _order = "delivery_date desc, batch_no asc, id desc"
    _rec_name = "display_name"

    _uniq_route_planning_batch = models.Constraint(
        "unique(batch_no, delivery_date)",
        "同一天内的排线批次号必须唯一。",
    )

    batch_no = fields.Char(string="批次号", required=True, index=True)
    delivery_date = fields.Date(string="配送日期", required=True, index=True)
    display_name = fields.Char(string="显示名称", compute="_compute_display_name", store=True)
    driver_name = fields.Char(string="司机姓名")
    driver_phone = fields.Char(string="司机电话")
    vehicle_no = fields.Char(string="车牌号")
    supplier_name = fields.Char(string="供应商名称")
    warehouse_name = fields.Char(string="仓库名称")
    import_task_id = fields.Many2one("logistics.import.task", string="最近导入任务", ondelete="set null", index=True)
    stop_line_ids = fields.One2many("logistics.route.planning.stop.line", "batch_id", string="停靠点")
    stop_count = fields.Integer(string="停靠点数", compute="_compute_counts", store=True)

    @api.depends("batch_no", "delivery_date")
    def _compute_display_name(self):
        for record in self:
            if record.batch_no and record.delivery_date:
                record.display_name = f"{record.batch_no} / {record.delivery_date}"
            else:
                record.display_name = record.batch_no or "排线批次草稿"

    @api.depends("stop_line_ids")
    def _compute_counts(self):
        for record in self:
            record.stop_count = len(record.stop_line_ids)


class LogisticsRoutePlanningStopLine(models.Model):
    _name = "logistics.route.planning.stop.line"
    _description = "排线停靠点"
    _order = "stop_seq asc, id asc"

    _uniq_route_planning_stop_seq = models.Constraint(
        "unique(batch_id, stop_seq)",
        "Route planning stop sequence must be unique within a batch.",
    )

    _uniq_route_planning_stop_waybill = models.Constraint(
        "unique(batch_id, waybill_no)",
        "Waybill number must be unique within the same route planning batch.",
    )

    batch_id = fields.Many2one("logistics.route.planning.batch", string="排线批次", required=True, ondelete="cascade", index=True)
    import_task_id = fields.Many2one("logistics.import.task", string="导入任务", ondelete="set null", index=True)
    import_task_line_id = fields.Many2one("logistics.import.task.line", string="导入任务行", ondelete="set null", index=True)
    batch_no = fields.Char(string="批次号", related="batch_id.batch_no", store=True, index=True)
    delivery_date = fields.Date(string="配送日期", related="batch_id.delivery_date", store=True, index=True)
    waybill_no = fields.Char(string="运单号", required=True, index=True)
    stop_seq = fields.Integer(string="停靠点顺序", required=True, index=True)
    store_name = fields.Char(string="门店名称", required=True)
    longitude = fields.Float(string="经度", digits=(16, 8), required=True)
    latitude = fields.Float(string="纬度", digits=(16, 8), required=True)
    address_detail = fields.Char(string="详细地址", required=True)
    contact_phone = fields.Char(string="门店联系电话")
    cargo_summary = fields.Text(string="货物信息")
    driver_name = fields.Char(string="司机姓名")
    driver_phone = fields.Char(string="司机电话")
    vehicle_no = fields.Char(string="车牌号")
    supplier_name = fields.Char(string="供应商名称")
    warehouse_name = fields.Char(string="仓库名称")
