from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WmsHandoverOrder(models.Model):
    _inherit = "wms.handover.order"

    order_refs_summary = fields.Char(string="订单号汇总", compute="_compute_chain_trace_fields", store=True, compute_sudo=True)
    waybill_nos_summary = fields.Char(string="运单号", compute="_compute_chain_trace_fields", store=True, compute_sudo=True)
    chain_step_summary = fields.Char(string="当前步骤", compute="_compute_chain_trace_fields", store=True, compute_sudo=True)

    @api.depends("outbound_task_id.stock_picking_id", "route_batch_id.stop_line_ids.waybill_no", "state")
    def _compute_chain_trace_fields(self):
        for record in self:
            picking = record.outbound_task_id.stock_picking_id if record.outbound_task_id else False
            sale_order = picking.sale_id if picking and "sale_id" in picking._fields else False
            waybills = record._chain_waybills()
            order_refs = [value for value in waybills.mapped("order_refs_summary") if value]
            if sale_order:
                order_refs.append(sale_order.name)
            waybill_nos = [waybill.waybill_no or waybill.name for waybill in waybills if waybill]
            if not waybill_nos and record.route_batch_id:
                waybill_nos = [value for value in record.route_batch_id.stop_line_ids.mapped("waybill_no") if value]
            record.order_refs_summary = " / ".join(dict.fromkeys(order_refs))
            record.waybill_nos_summary = " / ".join(dict.fromkeys(waybill_nos))
            record.chain_step_summary = record._chain_step_label()

    def _chain_step_label(self):
        self.ensure_one()
        labels = {
            "waiting_handover": _("待交接"),
            "handover_ing": _("交接中"),
            "handover_done": _("已交接"),
        }
        if self.route_batch_id:
            return _("已进入排线")
        return labels.get(self.state, self.state or "")

    def _chain_waybills(self):
        self.ensure_one()
        waybills = self.env["logistics.dispatch.waybill"].browse()
        picking = self.outbound_task_id.stock_picking_id if self.outbound_task_id else False
        if "logistics.dispatch.waybill.order.line" in self.env.registry and picking:
            waybills |= self.env["logistics.dispatch.waybill.order.line"].sudo().search(
                [("stock_picking_id", "=", picking.id)]
            ).mapped("waybill_id")
        if not waybills and self.route_batch_id:
            names = [name for name in self.route_batch_id.stop_line_ids.mapped("waybill_no") if name]
            if names:
                waybills |= self.env["logistics.dispatch.waybill"].sudo().search([("name", "in", names)])
        return waybills

    def action_create_dispatch_order(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条交接单记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        dispatch_order = self.env["tms.dispatch.order"].search([("handover_order_id", "=", self.id)], limit=1)
        if not dispatch_order:
            dispatch_order = self.env["tms.dispatch.order"].create_from_handover(self)
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="create_dispatch_order_from_handover",
                record=dispatch_order,
                note=_("Dispatch order created from handover order."),
                related_record=self,
            )
        return dispatch_order.action_open_record()

    def action_open_dispatch_orders(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条交接单记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Dispatch Orders"),
            "res_model": "tms.dispatch.order",
            "view_mode": "list,form",
            "domain": [("handover_order_id", "=", self.id)],
            "context": {"default_handover_order_id": self.id},
        }

    def action_open_chain_sale_orders(self):
        self.ensure_one()
        sale_orders = self.env["sale.order"].browse()
        picking = self.outbound_task_id.stock_picking_id if self.outbound_task_id else False
        if picking and "sale_id" in picking._fields and picking.sale_id:
            sale_orders |= picking.sale_id
        if "logistics.dispatch.waybill.order.line" in self.env.registry:
            domain = []
            if picking:
                domain = [("stock_picking_id", "=", picking.id)]
            elif sale_orders:
                domain = [("sale_order_id", "in", sale_orders.ids)]
            if domain:
                sale_orders |= self.env["logistics.dispatch.waybill.order.line"].sudo().search(domain).mapped("sale_order_id")
        return self._action_open_chain_records(_("销售订单"), "sale.order", sale_orders)

    def action_open_chain_outbound_tasks(self):
        self.ensure_one()
        return self._action_open_chain_records(_("出库任务"), "wms.outbound.task", self.outbound_task_id)

    def action_open_chain_waybills(self):
        self.ensure_one()
        waybills = self.env["logistics.dispatch.waybill"].browse()
        picking = self.outbound_task_id.stock_picking_id if self.outbound_task_id else False
        if "logistics.dispatch.waybill.order.line" in self.env.registry and picking:
            waybills |= self.env["logistics.dispatch.waybill.order.line"].sudo().search(
                [("stock_picking_id", "=", picking.id)]
            ).mapped("waybill_id")
        if not waybills and self.route_batch_id:
            names = [name for name in self.route_batch_id.stop_line_ids.mapped("waybill_no") if name]
            if names:
                waybills |= self.env["logistics.dispatch.waybill"].sudo().search([("name", "in", names)])
        return self._action_open_chain_records(_("运单"), "logistics.dispatch.waybill", waybills)

    def action_wms_trace_open_sale_orders(self):
        return self.action_open_chain_sale_orders()

    def action_wms_trace_open_outbound_tasks(self):
        return self.action_open_chain_outbound_tasks()

    def action_wms_trace_open_pick_tasks(self):
        self.ensure_one()
        return self._action_open_chain_records(_("拣货任务"), "wms.pick.task", self.outbound_task_id.pick_task_ids)

    def action_wms_trace_open_check_tasks(self):
        self.ensure_one()
        return self._action_open_chain_records(_("复核任务"), "wms.check.task", self.outbound_task_id.check_task_ids)

    def action_wms_trace_open_waybills(self):
        return self.action_open_chain_waybills()

    def action_wms_trace_open_route_batches(self):
        self.ensure_one()
        return self._action_open_chain_records(_("排线批次"), "logistics.route.planning.batch", self.route_batch_id)

    def _action_open_chain_records(self, title, model_name, records):
        records = records.exists()
        if not records:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("当前交接单暂未找到可打开的%s。") % title,
                    "type": "warning",
                },
            }
        action = {
            "type": "ir.actions.act_window",
            "name": title,
            "res_model": model_name,
            "target": "current",
        }
        if len(records) == 1:
            action.update({"view_mode": "form", "res_id": records.id})
        else:
            action.update({"view_mode": "list,form", "domain": [("id", "in", records.ids)]})
        return action

    def action_prepare_route_batch(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条交接单记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        if self.state != "handover_done":
            raise ValidationError(_("Handover order must be done before preparing a route batch."))
        outbound = self.outbound_task_id
        picking = outbound.stock_picking_id if outbound else False
        if not outbound or not picking:
            raise ValidationError(_("Handover order is missing an outbound task or stock picking."))
        partner = self._route_partner(picking)
        self._validate_route_partner(partner)
        waybills = self._ensure_route_waybills(picking, partner)
        if not waybills:
            raise ValidationError(_("No waybill is available for this handover order."))
        batch = self.route_batch_id or self._find_or_create_route_batch()
        self._ensure_route_stop_lines(batch, waybills, partner, picking)
        self.write(
            {
                "route_batch_id": batch.id,
                "weight_total": sum(waybills.mapped("total_goods_weight")) if "total_goods_weight" in waybills._fields else self.weight_total,
                "volume_total": sum(waybills.mapped("total_goods_volume")) if "total_goods_volume" in waybills._fields else self.volume_total,
            }
        )
        if "core.operation.audit.log" in self.env.registry:
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="handover_prepare_route_batch",
                record=batch,
                note=_("Route batch prepared from WMS handover order."),
                related_record=self,
                payload={"waybill_ids": waybills.ids, "stop_line_ids": batch.stop_line_ids.ids},
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("Route Batch"),
            "res_model": "logistics.route.planning.batch",
            "view_mode": "form",
            "res_id": batch.id,
        }

    def _find_or_create_route_batch(self):
        self.ensure_one()
        delivery_date = fields.Date.context_today(self)
        batch_no = "PDA-HO-%s-%s" % (self.id, delivery_date.strftime("%Y%m%d"))
        Batch = self.env["logistics.route.planning.batch"].sudo()
        batch = Batch.search([("batch_no", "=", batch_no), ("delivery_date", "=", delivery_date)], limit=1)
        if batch:
            return batch
        vals = {
            "batch_no": batch_no,
            "delivery_date": delivery_date,
            "warehouse_name": self.warehouse_id.display_name if self.warehouse_id else "",
            "driver_name": self._driver_name(),
            "driver_phone": self._driver_phone(),
            "vehicle_no": self._vehicle_no(),
        }
        if "warehouse_id" in Batch._fields:
            vals["warehouse_id"] = self.warehouse_id.id if self.warehouse_id else False
        if "driver_profile_id" in Batch._fields:
            vals["driver_profile_id"] = self.driver_profile_id.id if self.driver_profile_id else False
        if "vehicle_profile_id" in Batch._fields:
            vals["vehicle_profile_id"] = self.vehicle_profile_id.id if self.vehicle_profile_id else False
        return Batch.create(vals)

    def _ensure_route_waybills(self, picking, partner):
        Waybill = self.env["logistics.dispatch.waybill"].sudo()
        OrderLine = self.env["logistics.dispatch.waybill.order.line"].sudo()
        waybills = Waybill.browse()
        waybills |= OrderLine.search([("stock_picking_id", "=", picking.id)]).mapped("waybill_id")
        sale_order = picking.sale_id if "sale_id" in picking._fields else False
        if not waybills and sale_order:
            waybills |= OrderLine.search([("sale_order_id", "=", sale_order.id)]).mapped("waybill_id")
        if waybills:
            return waybills
        name = "WMS-HO-%s" % self.id
        waybill = Waybill.search([("name", "=", name)], limit=1)
        if not waybill:
            waybill = Waybill.create(
                {
                    "name": name,
                    "partner_id": partner.id,
                    "customer_id": partner.id,
                    "store_id": partner.id,
                    "warehouse_id": self.warehouse_id.id if self.warehouse_id else False,
                    "delivery_date": fields.Date.context_today(self),
                    "remark": self.note or picking.name,
                }
            )
        self._ensure_waybill_number(waybill)
        if not OrderLine.search([("waybill_id", "=", waybill.id), ("stock_picking_id", "=", picking.id)], limit=1):
            OrderLine.create(
                {
                    "waybill_id": waybill.id,
                    "stock_picking_id": picking.id,
                    "sale_order_id": sale_order.id if sale_order else False,
                    "source_doc_no": picking.name,
                    "sales_order_no": sale_order.name if sale_order else "",
                    "store_id": partner.id,
                    "goods_summary": self._picking_goods_summary(picking),
                    "qty_summary": sum(picking.move_ids.mapped("product_uom_qty")) if picking.move_ids else 0.0,
                }
            )
        return waybill

    def _ensure_route_stop_lines(self, batch, waybills, fallback_partner, picking):
        StopLine = self.env["logistics.route.planning.stop.line"].sudo()
        next_seq = max(batch.stop_line_ids.mapped("stop_seq") or [0]) + 1
        for waybill in waybills:
            waybill_no = self._ensure_waybill_number(waybill)
            if StopLine.search([("batch_id", "=", batch.id), ("waybill_no", "=", waybill_no)], limit=1):
                continue
            partner = waybill.partner_id or waybill.store_id or waybill.customer_id or fallback_partner
            self._validate_route_partner(partner)
            StopLine.create(self._prepare_stop_line_vals(batch, waybill, partner, picking, next_seq, waybill_no))
            next_seq += 1

    def _prepare_stop_line_vals(self, batch, waybill, partner, picking, stop_seq, waybill_no):
        return {
            "batch_id": batch.id,
            "waybill_no": waybill_no,
            "stop_seq": stop_seq,
            "store_name": partner.display_name,
            "longitude": partner.partner_longitude,
            "latitude": partner.partner_latitude,
            "address_detail": self._partner_address(partner),
            "contact_phone": self._partner_phone(partner),
            "cargo_summary": waybill.order_refs_summary or self._picking_goods_summary(picking),
            "driver_name": batch.driver_name or self._driver_name(),
            "driver_phone": batch.driver_phone or self._driver_phone(),
            "vehicle_no": batch.vehicle_no or self._vehicle_no(),
            "warehouse_name": batch.warehouse_name or (self.warehouse_id.display_name if self.warehouse_id else ""),
        }

    def _ensure_waybill_number(self, waybill):
        waybill_no = (
            waybill.name
            or (waybill.waybill_no if "waybill_no" in waybill._fields else False)
            or "WMS-HO-%s-WB-%s" % (self.id, waybill.id)
        )
        if "name" in waybill._fields and waybill.name != waybill_no:
            waybill.write({"name": waybill_no})
        return waybill_no

    def _route_partner(self, picking):
        outbound = self.outbound_task_id
        return (
            outbound.store_partner_id
            or (picking.store_partner_id if "store_partner_id" in picking._fields else False)
            or picking.partner_id
        )

    def _validate_route_partner(self, partner):
        if not partner:
            raise ValidationError(_("Route stop partner is required."))
        if not self._partner_address(partner):
            raise ValidationError(_("Route stop partner address_full is required."))
        if not partner.partner_longitude or not partner.partner_latitude:
            raise ValidationError(_("Route stop partner longitude and latitude are required."))

    def _partner_address(self, partner):
        return (
            getattr(partner, "address_full", False)
            or getattr(partner, "contact_address", False)
            or ", ".join([value for value in [partner.street, partner.street2, partner.city] if value])
        )

    def _partner_phone(self, partner):
        return getattr(partner, "contact_phone", False) or partner.phone or partner.mobile or ""

    def _picking_goods_summary(self, picking):
        product_names = [product.display_name for product in picking.move_ids.mapped("product_id")[:3]]
        suffix = "" if len(picking.move_ids.mapped("product_id")) <= 3 else "..."
        return "%s%s / %s" % (", ".join(product_names), suffix, picking.name)

    def _driver_name(self):
        driver = self.driver_profile_id
        return driver.driver_name or driver.display_name if driver else ""

    def _driver_phone(self):
        driver = self.driver_profile_id
        return driver.driver_phone if driver else ""

    def _vehicle_no(self):
        vehicle = self.vehicle_profile_id.vehicle_id if self.vehicle_profile_id else False
        return vehicle.license_plate or vehicle.name if vehicle else ""
