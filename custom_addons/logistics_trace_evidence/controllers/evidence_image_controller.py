import json

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

from ..services.image_storage_service import LogisticsEvidenceImageStorage


class LogisticsTraceEvidenceImageController(http.Controller):
    EVENT_TYPE_MAP = {
        "load": "finish_loading",
        "leave": "departed",
        "arrive": "arrive_store",
        "sign": "signoff",
        "exception": "exception_report",
    }

    STATUS_MAP = {
        "arrive_loading_point": "CURRENT",
        "start_loading": "CURRENT",
        "finish_loading": "CURRENT",
        "departed": "LEAVED",
        "arrive_store": "ARRIVED",
        "deliver_finish": "COMPLETED",
        "signoff": "COMPLETED",
        "exception_report": "EXCEPTION",
    }

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
            event_type = self._resolve_event_type(payload)
            trace_model = request.env["logistics.trace.event"].sudo()

            values = {
                "event_type": event_type,
                "submit_source": "mobile",
                "trace_time": payload.get("trace_time") or payload.get("occurred_at"),
                "remark": payload.get("remark"),
                "driver_name": payload.get("driver_name"),
                "plate_no": payload.get("vehicle_no") or payload.get("plate_no"),
                "location_text": payload.get("location_text"),
                "route_sequence": payload.get("route_sequence"),
                "source_channel": payload.get("source_channel") or "mini",
                "source_record_id": payload.get("source_record_id"),
                "is_exception": event_type == "exception_report",
            }

            batch = self._find_batch(payload)
            waybill = self._find_waybill(payload)
            if waybill:
                values["object_type"] = "waybill"
                values["waybill_id"] = waybill.id
                values["batch_id"] = waybill.batch_id.id
            elif batch:
                values["object_type"] = "batch"
                values["batch_id"] = batch.id
            else:
                raise UserError("waybill_id/waybill_no or batch_id/batch_no is required.")

            trace = trace_model.create(values)
            return self._json_response(
                {
                    "ok": True,
                    "message": "Trace event created successfully.",
                    "data": {
                        "trace_event_id": trace.id,
                        "trace_no": trace.name,
                        "object_type": trace.object_type,
                        "event_type": trace.event_type,
                        "batch_id": trace.batch_id.id if trace.batch_id else False,
                        "batch_no": trace.batch_id.name if trace.batch_id else False,
                        "waybill_id": trace.waybill_id.id if trace.waybill_id else False,
                        "waybill_no": trace.waybill_id.name if trace.waybill_id else False,
                        "state": trace.state,
                    },
                },
                status=200,
            )
        except UserError as exc:
            return self._json_response({"ok": False, "message": str(exc)}, status=400)

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
            trace_id = payload.get("trace_id") or payload.get("trace_event_id")
            if not trace_id:
                return self._json_response({"ok": False, "message": "trace_id is required."}, status=400)

            trace = request.env["logistics.trace.event"].sudo().browse(trace_id).exists()
            if not trace:
                return self._json_response({"ok": False, "message": "Trace event not found."}, status=404)

            evidence = request.env["logistics.trace.evidence"].sudo().create(
                {
                    "trace_event_id": trace.id,
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
                        "waybill_id": evidence.waybill_id.id if evidence.waybill_id else False,
                        "waybill_no": evidence.waybill_id.name if evidence.waybill_id else False,
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
            evidence = request.env["logistics.trace.evidence"].sudo().browse(evidence_id).exists()
            if not evidence:
                return self._json_response({"ok": False, "message": "Evidence not found."}, status=404)

            uploaded_file = request.httprequest.files.get("file")
            if not uploaded_file:
                return self._json_response({"ok": False, "message": "File field is required."}, status=400)

            evidence.upload_image_binary(
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
                        "image_access_key": evidence.image_access_key,
                        "preview_url": evidence.preview_url,
                        "full_url": evidence.full_url,
                        "state": evidence.state,
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
        methods=["POST"],
        csrf=False,
    )
    def upsert_waybill_stops(self, waybill_no, **kwargs):
        try:
            waybill = self._find_waybill({"waybill_no": waybill_no})
            if not waybill:
                return self._json_response({"ok": False, "message": "Waybill not found."}, status=404)

            payload = self._get_json_payload()
            stops_payload = payload.get("stops") or []
            if not isinstance(stops_payload, list) or not stops_payload:
                return self._json_response(
                    {"ok": False, "message": "stops must be a non-empty list."},
                    status=400,
                )

            stop_model = request.env["logistics.dispatch.waybill.stop"].sudo()
            existing_stops = stop_model.search([("waybill_id", "=", waybill.id)])
            stop_ids_to_keep = []

            for index, stop_payload in enumerate(stops_payload, start=1):
                stop_seq = int(stop_payload.get("stop_seq") or index)
                values = self._prepare_waybill_stop_values(
                    waybill=waybill,
                    stop_payload=stop_payload,
                    stop_seq=stop_seq,
                )
                stop = stop_model.search(
                    [("waybill_id", "=", waybill.id), ("stop_seq", "=", stop_seq)],
                    limit=1,
                )
                if stop:
                    stop.write(values)
                else:
                    stop = stop_model.create(values)
                stop_ids_to_keep.append(stop.id)

            (existing_stops - stop_model.browse(stop_ids_to_keep)).unlink()
            stops = stop_model.search([("waybill_id", "=", waybill.id)], order="stop_seq asc, id asc")
            traces = self._search_waybill_traces(waybill)
            payload = self._build_waybill_stops_payload(waybill, stops, traces)
            return self._json_response(
                {
                    "ok": True,
                    "message": "Waybill stops saved successfully.",
                    "data": payload,
                },
                status=200,
            )
        except (UserError, ValueError) as exc:
            return self._json_response({"ok": False, "message": str(exc)}, status=400)

    @http.route(
        ["/api/mini/logistics/waybills/<string:waybill_no>/stops"],
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def get_waybill_stops(self, waybill_no, **kwargs):
        waybill = self._find_waybill({"waybill_no": waybill_no})
        if not waybill:
            return self._json_response({"ok": False, "message": "Waybill not found."}, status=404)

        stops = request.env["logistics.dispatch.waybill.stop"].sudo().search(
            [("waybill_id", "=", waybill.id)],
            order="stop_seq asc, id asc",
        )
        if not stops:
            return self._json_response({"ok": False, "message": "Waybill stops not found."}, status=404)

        traces = self._search_waybill_traces(waybill)
        payload = self._build_waybill_stops_payload(waybill, stops, traces)
        return self._json_response({"ok": True, "data": payload}, status=200)

    @http.route(
        ["/logistics_trace/evidence-images/<string:image_access_key>"],
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def get_evidence_image(self, image_access_key, **kwargs):
        evidence = request.env["logistics.trace.evidence"].sudo().search(
            [("image_access_key", "=", image_access_key)],
            limit=1,
        )
        if not evidence:
            return request.not_found()

        storage = LogisticsEvidenceImageStorage(request.env)
        payload = storage.read_image(evidence)
        headers = [
            ("Content-Type", payload["content_type"]),
            ("Content-Length", str(payload["content_length"])),
        ]
        return request.make_response(payload["content"], headers=headers)

    def _resolve_event_type(self, payload):
        if payload.get("event_type"):
            return payload["event_type"]
        trace_type = payload.get("trace_type") or "arrive"
        return self.EVENT_TYPE_MAP.get(trace_type, trace_type)

    @staticmethod
    def _find_waybill(payload):
        waybill_model = request.env["logistics.dispatch.waybill"].sudo()
        if payload.get("waybill_id"):
            return waybill_model.browse(payload["waybill_id"]).exists()
        if payload.get("waybill_no"):
            return waybill_model.search([("name", "=", payload["waybill_no"])], limit=1)
        return waybill_model.browse()

    @staticmethod
    def _find_batch(payload):
        batch_model = request.env["logistics.dispatch.batch"].sudo()
        if payload.get("batch_id"):
            return batch_model.browse(payload["batch_id"]).exists()
        if payload.get("batch_no"):
            return batch_model.search([("name", "=", payload["batch_no"])], limit=1)
        return batch_model.browse()

    @staticmethod
    def _search_waybill_traces(waybill):
        return request.env["logistics.trace.event"].sudo().search(
            [("object_type", "=", "waybill"), ("waybill_id", "=", waybill.id)],
            order="route_sequence asc, trace_time asc, id asc",
        )

    def _prepare_waybill_stop_values(self, *, waybill, stop_payload, stop_seq):
        if not (stop_payload.get("store_name") or stop_payload.get("partner_id")):
            raise UserError("Each stop must provide store_name or partner_id.")
        return {
            "waybill_id": waybill.id,
            "stop_seq": stop_seq,
            "partner_id": stop_payload.get("partner_id"),
            "stock_picking_id": stop_payload.get("stock_picking_id"),
            "store_name": stop_payload.get("store_name") or "",
            "address": stop_payload.get("address"),
            "lat": stop_payload.get("lat"),
            "lng": stop_payload.get("lng"),
            "contact_name": stop_payload.get("contact_name"),
            "contact_phone": stop_payload.get("contact_phone"),
            "contact_list_json": json.dumps(stop_payload.get("contact_list") or [], ensure_ascii=False),
            "guide_url": stop_payload.get("guide_url"),
            "goods_info": stop_payload.get("goods_info"),
        }

    def _build_waybill_stops_payload(self, waybill, stop_records, traces):
        stops = []
        stop_index = {}
        for node_id, stop_record in enumerate(stop_records, start=1):
            stop = {
                "node_id": node_id,
                "stop_seq": stop_record.stop_seq or node_id,
                "store_name": stop_record.store_name,
                "address": stop_record.address,
                "lat": stop_record.lat,
                "lng": stop_record.lng,
                "contact_name": stop_record.contact_name,
                "contact_phone": stop_record.contact_phone,
                "contact_list": self._load_contact_list(stop_record),
                "guide_url": stop_record.guide_url,
                "goods_info": stop_record.goods_info or self._build_goods_info(stop_record.stock_picking_id),
                "status": "PENDING",
            }
            stops.append(stop)
            stop_index[stop_record.stop_seq] = stop

        for trace in traces:
            stop_seq = trace.route_sequence or 0
            if not stop_seq and len(stops) == 1:
                stop_seq = stops[0]["stop_seq"]
            stop = stop_index.get(stop_seq)
            if not stop:
                continue
            stop["status"] = self._merge_stop_status(stop["status"], trace.event_type, trace.is_exception)

        return {
            "waybill_id": waybill.id,
            "waybill_no": waybill.name,
            "batch_id": waybill.batch_id.id if waybill.batch_id else False,
            "batch_no": waybill.batch_id.name if waybill.batch_id else False,
            "driver_name": waybill.driver_employee_id.name if waybill.driver_employee_id else False,
            "vehicle_no": waybill.vehicle_id.license_plate if waybill.vehicle_id else False,
            "stops": stops,
        }

    @staticmethod
    def _load_contact_list(stop_record):
        if stop_record.contact_list_json:
            try:
                contact_list = json.loads(stop_record.contact_list_json)
                if isinstance(contact_list, list):
                    return contact_list[:3]
            except json.JSONDecodeError:
                pass
        if stop_record.contact_name or stop_record.contact_phone:
            return [{"name": stop_record.contact_name or "", "phone": stop_record.contact_phone or ""}]
        return []

    @staticmethod
    def _build_goods_info(picking):
        if not picking:
            return ""
        lines = []
        moves = picking.move_ids_without_package or picking.move_ids
        for move in moves[:5]:
            qty = move.product_uom_qty or move.quantity or 0
            uom_name = move.product_uom.name if move.product_uom else ""
            lines.append(
                f"{move.product_id.display_name} x {qty:g}{uom_name}" if uom_name else f"{move.product_id.display_name} x {qty:g}"
            )
        return "; ".join(lines)

    def _merge_stop_status(self, current_status, event_type, is_exception):
        if is_exception or event_type == "exception_report":
            return "EXCEPTION"
        priority = {
            "PENDING": 0,
            "CURRENT": 1,
            "LEAVED": 2,
            "ARRIVED": 3,
            "COMPLETED": 4,
            "EXCEPTION": 99,
        }
        next_status = self.STATUS_MAP.get(event_type, "PENDING")
        if priority.get(next_status, 0) >= priority.get(current_status, 0):
            return next_status
        return current_status

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
