import json
from urllib.parse import quote

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

from ..services.image_storage_service import LogisticsEvidenceImageStorage


class LogisticsTraceEvidenceImageController(http.Controller):
    GUIDE_URL_FIELDS = (
        "guide_url",
        "guide_link",
        "tencent_doc_url",
        "x_guide_url",
        "x_tencent_doc_url",
        "website",
    )

    @http.route(
        ["/api/mini/logistics/traces"],
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def create_trace_event(self, **kwargs):
        try:
            payload = self._get_json_payload()
            biz_type = payload.get("biz_type") or "waybill"
            values = {
                "biz_type": biz_type,
                "trace_type": payload.get("trace_type") or "arrive",
                "trace_source": "mini",
                "batch_no": payload.get("batch_no"),
                "waybill_no": payload.get("waybill_no"),
                "remark": payload.get("remark"),
                "driver_name": payload.get("driver_name"),
                "vehicle_no": payload.get("vehicle_no"),
                "location_text": payload.get("location_text"),
                "route_sequence": payload.get("route_sequence"),
            }
            if payload.get("partner_id"):
                values["partner_id"] = payload["partner_id"]
            if payload.get("stock_picking_id"):
                values["stock_picking_id"] = payload["stock_picking_id"]
            if payload.get("occurred_at"):
                values["occurred_at"] = payload["occurred_at"]

            trace = request.env["logistics.trace.event"].sudo().create(values)
            return self._json_response(
                {
                    "ok": True,
                    "message": "Trace event created successfully.",
                    "data": {
                        "trace_event_id": trace.id,
                        "trace_no": trace.name,
                        "biz_type": trace.biz_type,
                        "trace_type": trace.trace_type,
                        "batch_no": trace.batch_no,
                        "waybill_no": trace.waybill_no,
                        "state": trace.state,
                    },
                },
                status=200,
            )
        except UserError as exc:
            return self._json_response({"ok": False, "message": str(exc)}, status=400)

    @http.route(
        ["/api/mini/logistics/waybills/<string:waybill_no>/stops"],
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def get_waybill_stops(self, waybill_no, **kwargs):
        waybill_no = (waybill_no or "").strip()
        if not waybill_no:
            return self._json_response(
                {"ok": False, "message": "waybill_no is required."},
                status=400,
            )

        traces = request.env["logistics.trace.event"].sudo().search(
            [
                ("biz_type", "=", "waybill"),
                ("waybill_no", "=", waybill_no),
            ],
            order="route_sequence asc, occurred_at asc, id asc",
        )
        if not traces:
            return self._json_response(
                {"ok": False, "message": "Waybill not found."},
                status=404,
            )

        payload = self._build_waybill_stops_payload(traces)
        return self._json_response(
            {
                "ok": True,
                "data": payload,
            },
            status=200,
        )

    @http.route(
        ["/api/mini/logistics/evidences"],
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def create_evidence(self, **kwargs):
        try:
            payload = self._get_json_payload()
            trace_id = payload.get("trace_id")
            if not trace_id:
                return self._json_response(
                    {"ok": False, "message": "trace_id is required."},
                    status=400,
                )

            trace = (
                request.env["logistics.trace.event"]
                .sudo()
                .browse(trace_id)
                .exists()
            )
            if not trace:
                return self._json_response(
                    {"ok": False, "message": "Trace event not found."},
                    status=404,
                )

            evidence = request.env["logistics.trace.evidence"].sudo().create(
                {
                    "trace_id": trace.id,
                    "evidence_type": payload.get("evidence_type") or "image",
                    "remark": payload.get("remark"),
                }
            )
            return self._json_response(
                {
                    "ok": True,
                    "message": "Evidence created successfully.",
                    "data": {
                        "evidence_id": evidence.id,
                        "evidence_no": evidence.name,
                        "trace_event_id": trace.id,
                        "trace_no": trace.name,
                        "evidence_type": evidence.evidence_type,
                        "state": evidence.state,
                    },
                },
                status=200,
            )
        except UserError as exc:
            return self._json_response({"ok": False, "message": str(exc)}, status=400)

    @http.route(
        ["/api/mini/logistics/evidences/<int:evidence_id>/images"],
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def upload_evidence_image(self, evidence_id, **kwargs):
        try:
            evidence = (
                request.env["logistics.trace.evidence"]
                .sudo()
                .browse(evidence_id)
                .exists()
            )
            if not evidence:
                return self._json_response(
                    {"ok": False, "message": "Evidence not found."},
                    status=404,
                )

            uploaded_file = request.httprequest.files.get("file")
            if not uploaded_file:
                return self._json_response(
                    {"ok": False, "message": "File field is required."},
                    status=400,
                )

            image_record = evidence.upload_image_binary(
                file_name=uploaded_file.filename,
                content=uploaded_file.read(),
                content_type=uploaded_file.content_type or "application/octet-stream",
            )
            return self._json_response(
                {
                    "ok": True,
                    "message": "Image uploaded successfully.",
                    "data": {
                        "evidence_id": evidence.id,
                        "image_id": image_record.id,
                        "image_access_key": image_record.image_access_key,
                        "preview_url": image_record.preview_url,
                        "download_url": image_record.download_url,
                        "storage_status": image_record.storage_status,
                    },
                },
                status=200,
            )
        except UserError as exc:
            return self._json_response(
                {"ok": False, "message": str(exc)},
                status=400,
            )

    @http.route(
        ["/logistics_trace/evidence-images/<string:image_access_key>"],
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def get_evidence_image(self, image_access_key, download=False, **kwargs):
        image_record = (
            request.env["logistics.trace.evidence.image"]
            .sudo()
            .search([("image_access_key", "=", image_access_key)], limit=1)
        )
        if not image_record:
            return request.not_found()

        storage = LogisticsEvidenceImageStorage(request.env)
        payload = storage.read_image(image_record)
        file_name = payload["file_name"]
        disposition = "attachment" if download else "inline"
        encoded_name = quote(file_name)
        headers = [
            ("Content-Type", payload["content_type"]),
            ("Content-Length", str(payload["content_length"])),
            (
                "Content-Disposition",
                f"{disposition}; filename*=UTF-8''{encoded_name}",
            ),
        ]
        return request.make_response(payload["content"], headers=headers)

    @staticmethod
    def _json_response(payload, *, status):
        return request.make_response(
            json.dumps(payload),
            headers=[("Content-Type", "application/json")],
            status=status,
        )

    @staticmethod
    def _get_json_payload():
        return request.httprequest.get_json(silent=True) or {}

    def _build_waybill_stops_payload(self, traces):
        first_trace = traces[0]
        batch_no = next((trace.batch_no for trace in traces if trace.batch_no), first_trace.batch_no)
        driver_name = next(
            (trace.driver_name for trace in traces if trace.driver_name),
            first_trace.driver_name,
        )
        vehicle_no = next(
            (trace.vehicle_no for trace in traces if trace.vehicle_no),
            first_trace.vehicle_no,
        )
        stops = []
        stop_index = {}

        for trace in traces:
            partner = self._get_trace_partner(trace)
            key = (
                trace.route_sequence or 0,
                partner.id if partner else 0,
                trace.location_text or "",
            )
            stop = stop_index.get(key)
            if not stop:
                stop = self._create_stop_payload(
                    trace=trace,
                    partner=partner,
                    node_id=len(stops) + 1,
                )
                stops.append(stop)
                stop_index[key] = stop
            self._merge_trace_into_stop(stop, trace, partner)

        return {
            "waybill_no": first_trace.waybill_no,
            "batch_no": batch_no,
            "driver_name": driver_name,
            "vehicle_no": vehicle_no,
            "stops": stops,
        }

    def _create_stop_payload(self, *, trace, partner, node_id):
        contact_list = self._build_contact_list(partner)
        primary_contact = contact_list[0] if contact_list else {"name": None, "phone": None}
        lat, lng = self._get_partner_coordinates(partner)
        return {
            "node_id": node_id,
            "stop_seq": trace.route_sequence or node_id,
            "store_name": partner.name if partner else (trace.location_text or trace.waybill_no),
            "address": self._get_partner_address(partner) or trace.location_text,
            "lat": lat,
            "lng": lng,
            "contact_name": primary_contact["name"],
            "contact_phone": primary_contact["phone"],
            "contact_list": contact_list,
            "guide_url": self._get_guide_url(trace, partner),
            "goods_info": self._build_goods_info(trace.stock_picking_id),
            "status": self._trace_type_to_stop_status(trace.trace_type),
        }

    def _merge_trace_into_stop(self, stop, trace, partner):
        contact_list = self._build_contact_list(partner)
        if contact_list:
            stop["contact_list"] = contact_list
            stop["contact_name"] = contact_list[0]["name"]
            stop["contact_phone"] = contact_list[0]["phone"]

        address = self._get_partner_address(partner) or trace.location_text
        if address:
            stop["address"] = address

        lat, lng = self._get_partner_coordinates(partner)
        if lat is not None:
            stop["lat"] = lat
        if lng is not None:
            stop["lng"] = lng

        guide_url = self._get_guide_url(trace, partner)
        if guide_url:
            stop["guide_url"] = guide_url

        goods_info = self._build_goods_info(trace.stock_picking_id)
        if goods_info:
            stop["goods_info"] = goods_info

        stop["status"] = self._merge_stop_status(stop["status"], trace.trace_type, trace.is_exception)

    @staticmethod
    def _get_trace_partner(trace):
        if trace.partner_id:
            return trace.partner_id
        if trace.stock_picking_id and trace.stock_picking_id.partner_id:
            return trace.stock_picking_id.partner_id
        return request.env["res.partner"]

    @staticmethod
    def _get_partner_address(partner):
        if not partner:
            return None
        for field_name in ("contact_address", "street", "display_name"):
            value = getattr(partner, field_name, False)
            if value:
                return value
        return None

    @staticmethod
    def _get_partner_coordinates(partner):
        if not partner:
            return None, None
        lat = None
        lng = None
        if "partner_latitude" in partner._fields:
            lat = partner.partner_latitude
        if "partner_longitude" in partner._fields:
            lng = partner.partner_longitude
        return lat, lng

    def _get_guide_url(self, trace, partner):
        for record in (partner, trace.stock_picking_id if trace.stock_picking_id else None):
            if not record:
                continue
            for field_name in self.GUIDE_URL_FIELDS:
                if field_name in record._fields:
                    value = record[field_name]
                    if value:
                        return value
        return None

    @staticmethod
    def _build_contact_list(partner):
        if not partner:
            return []

        candidates = []
        seen = set()

        def append_contact(name, phone):
            if not (name or phone):
                return
            key = (name or "", phone or "")
            if key in seen:
                return
            seen.add(key)
            candidates.append({"name": name or "", "phone": phone or ""})

        append_contact(partner.name, partner.phone or partner.mobile)
        for child in partner.child_ids[:5]:
            append_contact(child.name, child.phone or child.mobile)

        return candidates[:3]

    @staticmethod
    def _build_goods_info(picking):
        if not picking:
            return ""

        lines = []
        moves = picking.move_ids_without_package or picking.move_ids
        for move in moves[:5]:
            qty = move.product_uom_qty or move.quantity or 0
            uom_name = move.product_uom.name if move.product_uom else ""
            if uom_name:
                lines.append(f"{move.product_id.display_name} x {qty:g}{uom_name}")
            else:
                lines.append(f"{move.product_id.display_name} x {qty:g}")

        return "; ".join(lines)

    @staticmethod
    def _trace_type_to_stop_status(trace_type):
        mapping = {
            "load": "loaded",
            "arrive": "arrived",
            "sign": "signed",
            "exception": "exception",
        }
        return mapping.get(trace_type, "pending")

    def _merge_stop_status(self, current_status, trace_type, is_exception):
        if is_exception or trace_type == "exception":
            return "exception"
        priority = {
            "pending": 0,
            "loaded": 1,
            "arrived": 2,
            "signed": 3,
            "exception": 99,
        }
        next_status = self._trace_type_to_stop_status(trace_type)
        if priority.get(next_status, 0) >= priority.get(current_status, 0):
            return next_status
        return current_status
