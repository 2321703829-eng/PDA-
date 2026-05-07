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
        methods=["POST"],
        csrf=False,
    )
    def upsert_waybill_stops(self, waybill_no, **kwargs):
        try:
            waybill_no = (waybill_no or "").strip()
            if not waybill_no:
                return self._json_response(
                    {"ok": False, "message": "waybill_no is required."},
                    status=400,
                )

            payload = self._get_json_payload()
            stops_payload = payload.get("stops") or []
            if not isinstance(stops_payload, list) or not stops_payload:
                return self._json_response(
                    {"ok": False, "message": "stops must be a non-empty list."},
                    status=400,
                )

            stop_model = request.env["logistics.waybill.stop"].sudo()
            existing_stops = stop_model.search([("waybill_no", "=", waybill_no)])
            stop_ids_to_keep = []

            for index, stop_payload in enumerate(stops_payload, start=1):
                stop_seq = int(stop_payload.get("stop_seq") or index)
                values = self._prepare_waybill_stop_values(
                    waybill_no=waybill_no,
                    stop_payload=stop_payload,
                    payload=payload,
                    stop_seq=stop_seq,
                )
                stop = stop_model.search(
                    [("waybill_no", "=", waybill_no), ("stop_seq", "=", stop_seq)],
                    limit=1,
                )
                if stop:
                    stop.write(values)
                else:
                    stop = stop_model.create(values)
                stop_ids_to_keep.append(stop.id)

            (existing_stops - stop_model.browse(stop_ids_to_keep)).unlink()
            stops = stop_model.search([("waybill_no", "=", waybill_no)], order="stop_seq asc, id asc")
            traces = self._search_waybill_traces(waybill_no)
            payload = self._build_waybill_stops_payload(stops, traces)
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
        waybill_no = (waybill_no or "").strip()
        if not waybill_no:
            return self._json_response(
                {"ok": False, "message": "waybill_no is required."},
                status=400,
            )

        stops = request.env["logistics.waybill.stop"].sudo().search(
            [("waybill_no", "=", waybill_no)],
            order="stop_seq asc, id asc",
        )
        if not stops:
            return self._json_response(
                {"ok": False, "message": "Waybill stops not found."},
                status=404,
            )

        traces = self._search_waybill_traces(waybill_no)
        payload = self._build_waybill_stops_payload(stops, traces)
        return self._json_response(
            {
                "ok": True,
                "data": payload,
            },
            status=200,
        )

    @http.route(
        ["/api/mini/logistics/waybills/<string:waybill_no>/stops/<int:stop_seq>/evidences"],
        type="http",
        auth="user",
        methods=["DELETE"],
        csrf=False,
    )
    def delete_waybill_stop_evidences(self, waybill_no, stop_seq, **kwargs):
        waybill_no = (waybill_no or "").strip()
        if not waybill_no:
            return self._json_response(
                {"ok": False, "message": "waybill_no is required."},
                status=400,
            )
        if stop_seq <= 0:
            return self._json_response(
                {"ok": False, "message": "stop_seq must be a positive integer."},
                status=400,
            )

        stop_records = request.env["logistics.waybill.stop"].sudo().search(
            [("waybill_no", "=", waybill_no)],
            order="stop_seq asc, id asc",
        )
        if not stop_records:
            return self._json_response(
                {"ok": False, "message": "Waybill stops not found."},
                status=404,
            )

        traces = self._search_waybill_traces(waybill_no)
        stop_traces = self._filter_traces_for_stop(stop_records, traces, stop_seq)
        if not stop_traces:
            return self._json_response(
                {
                    "ok": True,
                    "message": "No evidences found for the selected stop.",
                    "data": {
                        "waybill_no": waybill_no,
                        "stop_seq": stop_seq,
                        "deleted_evidence_count": 0,
                        "deleted_image_count": 0,
                    },
                },
                status=200,
            )

        evidences = (
            request.env["logistics.trace.evidence"]
            .sudo()
            .search(
                [
                    ("trace_id", "in", stop_traces.ids),
                    ("evidence_type", "in", ("image", "sign")),
                ]
            )
        )
        deleted_evidence_count = len(evidences)
        deleted_image_count = sum(len(evidence.image_ids) for evidence in evidences)
        if evidences:
            evidences.unlink()

        return self._json_response(
            {
                "ok": True,
                "message": "Stop evidences deleted successfully.",
                "data": {
                    "waybill_no": waybill_no,
                    "stop_seq": stop_seq,
                    "deleted_evidence_count": deleted_evidence_count,
                    "deleted_image_count": deleted_image_count,
                },
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

    @staticmethod
    def _search_waybill_traces(waybill_no):
        return request.env["logistics.trace.event"].sudo().search(
            [
                ("biz_type", "=", "waybill"),
                ("waybill_no", "=", waybill_no),
            ],
            order="route_sequence asc, occurred_at asc, id asc",
        )

    def _prepare_waybill_stop_values(self, *, waybill_no, stop_payload, payload, stop_seq):
        if not (stop_payload.get("store_name") or stop_payload.get("partner_id")):
            raise UserError("Each stop must provide store_name or partner_id.")
        return {
            "waybill_no": waybill_no,
            "batch_no": stop_payload.get("batch_no") or payload.get("batch_no"),
            "stop_seq": stop_seq,
            "store_name": stop_payload.get("store_name") or "",
            "address": stop_payload.get("address"),
            "lat": stop_payload.get("lat"),
            "lng": stop_payload.get("lng"),
            "contact_name": stop_payload.get("contact_name"),
            "contact_phone": stop_payload.get("contact_phone"),
            "contact_list_json": json.dumps(stop_payload.get("contact_list") or [], ensure_ascii=False),
            "guide_url": stop_payload.get("guide_url"),
            "goods_info": stop_payload.get("goods_info"),
            "driver_name": stop_payload.get("driver_name") or payload.get("driver_name"),
            "vehicle_no": stop_payload.get("vehicle_no") or payload.get("vehicle_no"),
            "partner_id": stop_payload.get("partner_id"),
            "stock_picking_id": stop_payload.get("stock_picking_id"),
        }

    def _build_waybill_stops_payload(self, stop_records, traces):
        first_stop = stop_records[0]
        first_trace = traces[:1]
        first_trace = first_trace[0] if first_trace else None
        batch_no = first_stop.batch_no or (first_trace.batch_no if first_trace else None)
        driver_name = first_stop.driver_name or (first_trace.driver_name if first_trace else None)
        vehicle_no = first_stop.vehicle_no or (first_trace.vehicle_no if first_trace else None)
        stops = []
        stop_index = {}

        for node_id, stop_record in enumerate(stop_records, start=1):
            stop = self._create_stop_payload_from_record(stop_record=stop_record, node_id=node_id)
            stops.append(stop)
            stop_index[stop_record.stop_seq] = stop

        for trace in traces:
            stop_seq = trace.route_sequence or 0
            if not stop_seq and len(stops) == 1:
                stop_seq = stops[0]["stop_seq"]
            stop = stop_index.get(stop_seq)
            if not stop:
                continue
            self._merge_trace_into_stop(stop, trace)

        return {
            "waybill_no": first_stop.waybill_no,
            "batch_no": batch_no,
            "driver_name": driver_name,
            "vehicle_no": vehicle_no,
            "stops": stops,
        }

    def _create_stop_payload_from_record(self, *, stop_record, node_id):
        contact_list = self._load_contact_list(stop_record)
        primary_contact = contact_list[0] if contact_list else {"name": None, "phone": None}
        return {
            "node_id": node_id,
            "stop_seq": stop_record.stop_seq or node_id,
            "store_name": stop_record.store_name,
            "address": stop_record.address,
            "lat": stop_record.lat,
            "lng": stop_record.lng,
            "contact_name": primary_contact["name"],
            "contact_phone": primary_contact["phone"],
            "contact_list": contact_list,
            "guide_url": stop_record.guide_url,
            "goods_info": stop_record.goods_info or self._build_goods_info(stop_record.stock_picking_id),
            "status": "PENDING",
            "evidence_images": [],
        }

    def _merge_trace_into_stop(self, stop, trace):
        stop["status"] = self._merge_stop_status(stop["status"], trace.trace_type, trace.is_exception)
        stop["evidence_images"] = self._merge_stop_evidence_images(
            stop.get("evidence_images") or [],
            trace,
        )

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
            return [
                {
                    "name": stop_record.contact_name or "",
                    "phone": stop_record.contact_phone or "",
                }
            ]
        return []

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

    def _filter_traces_for_stop(self, stop_records, traces, stop_seq):
        only_stop_seq = stop_records.mapped("stop_seq")
        single_stop_seq = only_stop_seq[0] if len(only_stop_seq) == 1 else None
        return traces.filtered(
            lambda trace: (trace.route_sequence or single_stop_seq or 0) == stop_seq
        )

    def _merge_stop_evidence_images(self, current_images, trace):
        merged = list(current_images)
        seen_keys = {
            (image.get("image_id"), image.get("image_access_key"))
            for image in merged
        }
        for evidence in trace.sudo().mapped("evidence_ids"):
            for image in evidence.image_ids:
                key = (image.id, image.image_access_key)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                merged.append(
                    {
                        "image_id": image.id,
                        "evidence_id": evidence.id,
                        "trace_event_id": trace.id,
                        "trace_type": trace.trace_type,
                        "image_access_key": image.image_access_key,
                        "file_name": image.source_filename or image.stored_file_name,
                        "preview_url": image.preview_url,
                        "download_url": image.download_url,
                        "storage_status": image.storage_status,
                    }
                )
        return merged

    @staticmethod
    def _trace_type_to_stop_status(trace_type):
        mapping = {
            "load": "CURRENT",
            "leave": "LEAVED",
            "arrive": "ARRIVED",
            "sign": "COMPLETED",
            "exception": "EXCEPTION",
        }
        return mapping.get(trace_type, "PENDING")

    def _merge_stop_status(self, current_status, trace_type, is_exception):
        if is_exception or trace_type == "exception":
            return "EXCEPTION"
        priority = {
            "PENDING": 0,
            "CURRENT": 1,
            "LEAVED": 2,
            "ARRIVED": 3,
            "COMPLETED": 4,
            "EXCEPTION": 99,
        }
        next_status = self._trace_type_to_stop_status(trace_type)
        if priority.get(next_status, 0) >= priority.get(current_status, 0):
            return next_status
        return current_status
