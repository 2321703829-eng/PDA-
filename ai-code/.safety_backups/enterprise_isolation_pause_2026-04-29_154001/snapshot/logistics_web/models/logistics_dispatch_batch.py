from odoo import fields, models


class LogisticsDispatchBatch(models.Model):
    _inherit = "logistics.dispatch.batch"

    def action_open_driver_route_export(self):
        self.ensure_one()
        action = self.env.ref("logistics_web.action_logistics_web_import_center").sudo().read()[0]
        delivery_dates = sorted(
            {
                fields.Date.to_string(delivery_date)
                for delivery_date in self.waybill_ids.mapped("delivery_date")
                if delivery_date
            }
        )
        delivery_date = False
        hint = False
        if len(delivery_dates) == 1:
            delivery_date = delivery_dates[0]
        elif len(delivery_dates) > 1:
            hint = "当前批次下存在多个配送日期，请先确认后再导出当天路线。"
        elif self.planned_depart_time:
            delivery_date = fields.Datetime.to_datetime(self.planned_depart_time).date().isoformat()
            hint = "当前批次没有明确运单配送日期，已按计划发车日期预填导出日期。"
        else:
            hint = "当前批次未识别到明确配送日期，请先确认后再导出当天路线。"

        action["params"] = {
            "source_model": "logistics.dispatch.waybill",
            "driver_export_delivery_date": delivery_date,
            "driver_export_batch_no": self.name or "",
            "driver_export_hint": hint,
        }
        return action
