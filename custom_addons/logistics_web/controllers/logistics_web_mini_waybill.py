import hashlib
import json

from odoo import fields, http
from odoo.http import request

from .logistics_web_mini_trace import LogisticsMiniApiAuthMixin


class LogisticsMiniWaybillController(http.Controller, LogisticsMiniApiAuthMixin):
    @http.route(
        [
            "/api/mini/logistics/waybills/<string:no>/stops",
            "/<string:lang>/api/mini/logistics/waybills/<string:no>/stops",
        ],
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_waybill_stops(self, no, lang=None, **kwargs):
        payload = dict(request.httprequest.args or {})
        try:
            self._ensure_mini_token(payload)
        except PermissionError as error:
            return self._json_response({"ok": False, "message": str(error)}, status=401)
        waybill_model = request.env["logistics.dispatch.waybill"].sudo()
        batch_model = request.env["logistics.dispatch.batch"].sudo()

        waybill = waybill_model.search([("name", "=", no)], limit=1)
        if waybill:
            payload = self._build_waybill_payload(waybill)
            return self._json_response(payload, status=200)

        batch = batch_model.search([("name", "=", no)], limit=1)
        if batch:
            payload = self._build_batch_payload(batch)
            return self._json_response(payload, status=200)

        return self._json_response(
            {
                "ok": False,
                "message": f"Waybill or batch not found: {no}",
            },
            status=404,
        )

    def _build_waybill_payload(self, waybill):
        stops = self._build_stops_for_waybills([waybill], is_batch_route=False)
        return {
            "ok": True,
            "data": {
                "waybill_no": waybill.name or "",
                "batch_no": waybill.batch_id.name or "",
                "is_batch_route": False,
                "route_cache_key": self._build_route_cache_key([waybill], stops=stops, batch=waybill.batch_id),
                "stops": stops,
            },
        }

    def _build_batch_payload(self, batch):
        waybills = batch.waybill_ids.sorted(key=lambda rec: (rec.route_seq or 0, rec.id))
        stops = self._build_stops_for_waybills(waybills, is_batch_route=True)
        return {
            "ok": True,
            "data": {
                "waybill_no": "",
                "batch_no": batch.name or "",
                "is_batch_route": True,
                "route_cache_key": self._build_route_cache_key(waybills, stops=stops, batch=batch),
                "stops": stops,
            },
        }

    def _build_stops_for_waybills(self, waybills, *, is_batch_route):
        stops = []
        current_waybill_id = self._pick_current_waybill_id(waybills) if is_batch_route else False
        for waybill in waybills:
            customer_lines = waybill.customer_line_ids.sorted(key=lambda rec: (rec.stop_seq_in_waybill or 0, rec.id))
            evidence_images = self._collect_evidence_images(waybill)
            for customer_line in customer_lines:
                status = self._build_stop_status(
                    waybill,
                    is_current_candidate=bool(current_waybill_id and waybill.id == current_waybill_id),
                )
                stops.append(
                    {
                        "node_id": self._build_node_id(waybill, customer_line),
                        "stop_seq": customer_line.stop_seq_in_waybill or waybill.route_seq or 0,
                        "waybill_no": waybill.name or "",
                        "store_name": customer_line.customer_name_snapshot
                        or customer_line.store_name
                        or customer_line.partner_name
                        or "",
                        "address": customer_line.address_full_snapshot or "",
                        "contact_name": customer_line.contact_name_snapshot or "",
                        "contact_phone": customer_line.contact_phone_snapshot or "",
                        "lat": customer_line.latitude_snapshot or 0.0,
                        "lng": customer_line.longitude_snapshot or 0.0,
                        "goods_info": self._build_goods_info(customer_line),
                        "status": status,
                        "evidence_images": evidence_images,
                    }
                )
        return stops

    def _pick_current_waybill_id(self, waybills):
        for waybill in waybills:
            status = self._build_stop_status(waybill, is_current_candidate=False)
            if status in {"PENDING", "CURRENT", "ARRIVED", "LEAVED"}:
                return waybill.id
        return False

    def _build_stop_status(self, waybill, *, is_current_candidate=False):
        events = waybill.trace_event_ids.filtered(lambda rec: rec.state == "submitted")
        event_types = set(events.mapped("event_type"))
        if waybill.state in {"signed", "done"} or {"deliver_finish", "signoff"} & event_types:
            return "COMPLETED"
        if waybill.state == "arrived" or "arrive_store" in event_types:
            return "ARRIVED"
        if waybill.state == "in_transit" or "departed" in event_types:
            return "LEAVED"
        if is_current_candidate:
            return "CURRENT"
        return "PENDING"

    def _build_node_id(self, waybill, customer_line):
        line_no = customer_line.customer_line_no or str(customer_line.id)
        return f"{waybill.name}:{line_no}"

    def _build_goods_info(self, customer_line):
        goods_lines = customer_line.goods_line_ids.sorted(key=lambda rec: (rec.sequence, rec.id))
        if not goods_lines:
            return ""
        if len(goods_lines) == 1:
            line = goods_lines[0]
            qty = self._format_number(line.quantity)
            unit = line.uom_name or line.small_unit_name or ""
            name = line.goods_name or line.product_name_snapshot or ""
            return f"{name} {qty}{unit}".strip()
        names = [line.goods_name or line.product_name_snapshot or "" for line in goods_lines[:2]]
        names = [name for name in names if name]
        prefix = "、".join(names)
        if len(goods_lines) > 2:
            prefix = f"{prefix}等{len(goods_lines)}种货物" if prefix else f"{len(goods_lines)}种货物"
        total_qty = self._format_number(customer_line.total_goods_qty)
        return f"{prefix} / 总数量 {total_qty}".strip(" /")

    def _collect_evidence_images(self, waybill):
        items = []
        seen = set()
        evidences = waybill.evidence_ids.sorted(
            key=lambda rec: (
                fields.Datetime.to_string(rec.uploaded_at) or "",
                rec.sequence,
                rec.id,
            ),
            reverse=True,
        )
        for evidence in evidences:
            if "image_ids" in evidence._fields:
                image_records = evidence.image_ids.filtered(
                    lambda rec: getattr(rec, "storage_status", "active") != "deleted"
                ).sorted(
                    key=lambda rec: (
                        rec.sequence,
                        rec.id,
                    )
                )
                if image_records:
                    for image in image_records:
                        image_key = (image.image_access_key or "").strip()
                        preview_url = self._normalize_preview_url(
                            image_key,
                            (image.preview_url or image.full_url or "").strip(),
                        )
                        if not image_key and not preview_url:
                            continue
                        dedupe_key = image_key or preview_url
                        if dedupe_key in seen:
                            continue
                        seen.add(dedupe_key)
                        items.append(
                            {
                                "image_access_key": image_key,
                                "preview_url": preview_url
                                or (f"/logistics_trace/evidence-images/{image_key}" if image_key else ""),
                            }
                        )
                    continue
            image_key = (evidence.image_access_key or "").strip()
            preview_url = self._normalize_preview_url(
                image_key,
                (evidence.preview_url or evidence.full_url or "").strip(),
            )
            if not image_key and not preview_url:
                continue
            dedupe_key = image_key or preview_url
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            items.append(
                {
                    "image_access_key": image_key,
                    "preview_url": preview_url
                    or (f"/logistics_trace/evidence-images/{image_key}" if image_key else ""),
                }
            )
        return items

    def _normalize_preview_url(self, image_key, preview_url):
        if image_key:
            return f"/logistics_trace/evidence-images/{image_key}"
        return preview_url

    def _build_route_cache_key(self, waybills, *, stops, batch):
        batch_part = batch.name if batch else ""
        latest_write = max(
            [
                fields.Datetime.to_string(rec.write_date or rec.create_date or fields.Datetime.now())
                for rec in waybills
            ]
            or [""]
        )
        raw = "|".join(
            [
                batch_part,
                ",".join(str(rec.id) for rec in waybills),
                str(len(stops)),
                latest_write,
            ]
        )
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:24]

    def _format_number(self, value):
        if value is None:
            return "0"
        if float(value).is_integer():
            return str(int(value))
        return f"{value:.4f}".rstrip("0").rstrip(".")

    def _json_response(self, payload, *, status):
        return request.make_response(
            json.dumps(payload, ensure_ascii=False),
            headers=[("Content-Type", "application/json")],
            status=status,
        )
