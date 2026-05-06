import hashlib
import json
import os

from odoo import fields, http
from odoo.http import request


class LogisticsMiniApiAuthMixin:
    MINI_TOKEN_HEADERS = (
        "X-Mini-Api-Token",
        "X-Mini-Token",
        "X-App-Token",
    )

    def _is_mini_token_enabled(self):
        raw = (
            request.env["ir.config_parameter"].sudo().get_param("logistics_web.mini_api_token_enabled")
            or os.getenv("LOGISTICS_MINI_API_TOKEN_ENABLED")
            or ""
        ).strip().lower()
        return raw in {"1", "true", "yes", "on"}

    def _get_configured_mini_token(self):
        token = (
            request.env["ir.config_parameter"].sudo().get_param("logistics_web.mini_api_token")
            or os.getenv("LOGISTICS_MINI_API_TOKEN")
            or ""
        ).strip()
        return token

    def _get_request_mini_token(self, payload):
        for header_name in self.MINI_TOKEN_HEADERS:
            header_value = request.httprequest.headers.get(header_name)
            if header_value:
                return header_value.strip()
        token = self._pick_first(
            payload,
            [
                "mini_api_token",
                "miniApiToken",
                "token",
                "app_token",
                "appToken",
            ],
        )
        return str(token).strip() if token else ""

    def _ensure_mini_token(self, payload):
        if not self._is_mini_token_enabled():
            return
        expected = self._get_configured_mini_token()
        if not expected:
            raise PermissionError("Mini api token is not configured.")
        actual = self._get_request_mini_token(payload)
        if actual != expected:
            raise PermissionError("Invalid mini api token.")


class LogisticsMiniTraceController(http.Controller, LogisticsMiniApiAuthMixin):
    @http.route(
        [
            "/api/mini/logistics/traces",
            "/<string:lang>/api/mini/logistics/traces",
        ],
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def create_trace(self, lang=None, **kwargs):
        payload = self._collect_request_payload()
        try:
            self._ensure_mini_token(payload)
        except PermissionError as error:
            return self._json_response({"ok": False, "message": str(error)}, status=401)
        biz_type = (self._pick_first(payload, ["biz_type", "bizType"]) or "waybill").strip()
        if biz_type not in {"waybill", "batch", ""}:
            return self._json_response(
                {
                    "ok": False,
                    "message": f"Unsupported biz_type: {biz_type}",
                },
                status=400,
            )
        waybill, customer_line = self._resolve_target(payload)
        if not waybill:
            return self._json_response(
                {
                    "ok": False,
                    "message": "Waybill or stop target not found.",
                },
                status=404,
            )

        trace_event = request.env["logistics.trace.event"].sudo().create(
            self._build_trace_event_vals(waybill, payload)
        )

        return self._json_response(
            {
                "ok": True,
                "data": {
                    "trace_id": trace_event.id,
                    "trace_event_id": trace_event.id,
                    "waybill_no": waybill.name or "",
                    "batch_no": waybill.batch_id.name or "",
                    "node_id": self._build_node_id(waybill, customer_line),
                    "stop_seq": customer_line.stop_seq_in_waybill if customer_line else (waybill.route_seq or 0),
                },
            },
            status=200,
        )

    @http.route(
        [
            "/api/mini/logistics/evidences",
            "/<string:lang>/api/mini/logistics/evidences",
        ],
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def create_evidence(self, lang=None, **kwargs):
        payload = self._collect_request_payload()
        try:
            self._ensure_mini_token(payload)
        except PermissionError as error:
            return self._json_response({"ok": False, "message": str(error)}, status=401)
        trace_event = self._resolve_trace_event(payload)
        if not trace_event:
            return self._json_response(
                {
                    "ok": False,
                    "message": "Trace event not found.",
                },
                status=404,
            )
        evidence = self._get_or_create_evidence(trace_event, payload)
        return self._json_response(
            {
                "ok": True,
                "data": {
                    "evidence_id": evidence.id,
                    "trace_event_id": trace_event.id,
                    "waybill_no": trace_event.waybill_id.name or "",
                },
            },
            status=200,
        )

    @http.route(
        [
            "/api/mini/logistics/evidences/<int:evidence_id>/images",
            "/<string:lang>/api/mini/logistics/evidences/<int:evidence_id>/images",
        ],
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def upload_evidence_images(self, evidence_id, lang=None, **kwargs):
        payload = self._collect_request_payload()
        try:
            self._ensure_mini_token(payload)
        except PermissionError as error:
            return self._json_response({"ok": False, "message": str(error)}, status=401)
        evidence = request.env["logistics.trace.evidence"].sudo().browse(evidence_id)
        if not evidence.exists():
            return self._json_response(
                {
                    "ok": False,
                    "message": "Evidence not found.",
                },
                status=404,
            )
        uploaded_images = self._handle_uploaded_files(evidence)
        return self._json_response(
            {
                "ok": True,
                "data": {
                    "evidence_id": evidence.id,
                    "image_count": len(uploaded_images),
                    "images": uploaded_images,
                },
            },
            status=200,
        )

    def _collect_request_payload(self):
        payload = {}
        json_payload = request.httprequest.get_json(silent=True)
        if isinstance(json_payload, dict):
            payload.update(json_payload)
        for key in request.httprequest.form.keys():
            values = request.httprequest.form.getlist(key)
            payload[key] = values if len(values) > 1 else values[0]
        return payload

    def _resolve_target(self, payload):
        customer_line = self._resolve_customer_line(payload)
        if customer_line:
            return customer_line.waybill_id, customer_line

        waybill_model = request.env["logistics.dispatch.waybill"].sudo()
        batch_model = request.env["logistics.dispatch.batch"].sudo()
        no = self._pick_first(
            payload,
            [
                "waybill_no",
                "waybillNo",
                "no",
                "shipment_no",
                "shipmentNo",
                "biz_no",
                "bizNo",
            ],
        )
        if no:
            waybill = waybill_model.search([("name", "=", str(no).strip())], limit=1)
            if waybill:
                customer_line = waybill.customer_line_ids.sorted(
                    key=lambda rec: (rec.stop_seq_in_waybill or 0, rec.id)
                )[:1]
                customer_line = customer_line[0] if customer_line else False
                return waybill, customer_line

            batch = batch_model.search([("name", "=", str(no).strip())], limit=1)
            if batch:
                stop_seq = self._coerce_int(
                    self._pick_first(
                        payload,
                        [
                            "stop_seq",
                            "stopSeq",
                            "route_seq",
                            "routeSeq",
                            "route_sequence",
                            "routeSequence",
                        ],
                    )
                )
                waybill = self._resolve_waybill_from_batch(batch, stop_seq)
                if waybill:
                    customer_line = waybill.customer_line_ids.sorted(
                        key=lambda rec: (rec.stop_seq_in_waybill or 0, rec.id)
                    )[:1]
                    customer_line = customer_line[0] if customer_line else False
                    return waybill, customer_line

        batch_no = self._pick_first(payload, ["batch_no", "batchNo"])
        if batch_no:
            batch = batch_model.search([("name", "=", str(batch_no).strip())], limit=1)
            if batch:
                stop_seq = self._coerce_int(
                    self._pick_first(
                        payload,
                        [
                            "stop_seq",
                            "stopSeq",
                            "route_seq",
                            "routeSeq",
                            "route_sequence",
                            "routeSequence",
                        ],
                    )
                )
                waybill = self._resolve_waybill_from_batch(batch, stop_seq)
                if waybill:
                    customer_line = waybill.customer_line_ids.sorted(
                        key=lambda rec: (rec.stop_seq_in_waybill or 0, rec.id)
                    )[:1]
                    customer_line = customer_line[0] if customer_line else False
                    return waybill, customer_line

        return False, False

    def _resolve_customer_line(self, payload):
        customer_line_model = request.env["logistics.dispatch.waybill.customer.line"].sudo()
        node_id = self._pick_first(payload, ["node_id", "nodeId"])
        if node_id and ":" in str(node_id):
            waybill_no, line_no = str(node_id).split(":", 1)
            domain = [
                ("waybill_id.name", "=", waybill_no.strip()),
                "|",
                ("customer_line_no", "=", line_no.strip()),
                ("stop_seq_in_waybill", "=", self._coerce_int(line_no)),
            ]
            customer_line = customer_line_model.search(domain, limit=1)
            if customer_line:
                return customer_line

        line_no = self._pick_first(
            payload,
            [
                "customer_line_no",
                "customerLineNo",
                "stop_seq",
                "stopSeq",
                "route_seq",
                "routeSeq",
                "route_sequence",
                "routeSequence",
            ],
        )
        waybill_no = self._pick_first(payload, ["waybill_no", "waybillNo"])
        if waybill_no and line_no is not None:
            customer_line = customer_line_model.search(
                [
                    ("waybill_id.name", "=", str(waybill_no).strip()),
                    "|",
                    ("customer_line_no", "=", str(line_no).strip()),
                    ("stop_seq_in_waybill", "=", self._coerce_int(line_no)),
                ],
                limit=1,
            )
            if customer_line:
                return customer_line
        return False

    def _resolve_waybill_from_batch(self, batch, stop_seq):
        waybills = batch.waybill_ids.sorted(key=lambda rec: (rec.route_seq or 0, rec.id))
        if stop_seq is not None:
            matched = waybills.filtered(lambda rec: (rec.route_seq or 0) == stop_seq)
            if matched:
                return matched[0]
        return waybills[:1][0] if waybills else False

    def _build_trace_event_vals(self, waybill, payload):
        event_type = self._normalize_trace_type(
            self._pick_first(payload, ["event_type", "eventType", "trace_type", "traceType"])
        )
        remark = self._pick_first(payload, ["remark", "trace_remark", "memo"]) or False
        location_text = self._pick_first(
            payload,
            [
                "location_text",
                "locationText",
                "address",
                "detail_address",
                "detailAddress",
            ],
        ) or False
        source_record_id = self._pick_first(
            payload,
            [
                "source_record_id",
                "sourceRecordId",
                "trace_no",
                "traceNo",
            ],
        ) or False
        return {
            "event_type": event_type,
            "object_type": "waybill",
            "waybill_id": waybill.id,
            "batch_id": waybill.batch_id.id,
            "trace_time": fields.Datetime.now(),
            "submit_source": "mobile",
            "state": "submitted",
            "location_text": location_text,
            "plate_no": waybill.vehicle_id.license_plate if waybill.vehicle_id else False,
            "driver_name": waybill.driver_employee_id.name if waybill.driver_employee_id else False,
            "remark": remark,
            "source_channel": "mini",
            "source_record_id": source_record_id,
        }

    def _resolve_trace_event(self, payload):
        trace_event_model = request.env["logistics.trace.event"].sudo()
        trace_event_id = self._coerce_int(
            self._pick_first(payload, ["trace_event_id", "traceEventId", "trace_id", "traceId"])
        )
        if trace_event_id:
            record = trace_event_model.browse(trace_event_id)
            if record.exists():
                return record
        return False

    def _get_or_create_evidence(self, trace_event, payload):
        evidence_model = request.env["logistics.trace.evidence"].sudo()
        remark = self._pick_first(payload, ["remark", "memo"]) or False
        client_request_id = self._extract_client_request_id(payload)

        if client_request_id:
            existing = evidence_model.search(
                [
                    ("trace_event_id", "=", trace_event.id),
                    ("client_request_id", "=", client_request_id),
                ],
                order="id desc",
                limit=1,
            )
            if existing:
                return existing

        fallback = evidence_model.search(
            [
                ("trace_event_id", "=", trace_event.id),
                ("image_count", "=", 0),
                ("remark", "=", remark or False),
            ],
            order="id desc",
            limit=1,
        )
        if fallback and fallback.uploaded_at:
            uploaded_at = fields.Datetime.to_datetime(fallback.uploaded_at)
            if uploaded_at and abs((fields.Datetime.now() - uploaded_at).total_seconds()) <= 300:
                if client_request_id and not fallback.client_request_id:
                    fallback.write({"client_request_id": client_request_id})
                return fallback

        return evidence_model.create(
            {
                "trace_event_id": trace_event.id,
                "uploaded_at": fields.Datetime.now(),
                "remark": remark,
                "client_request_id": client_request_id or False,
            }
        )

    def _extract_client_request_id(self, payload):
        value = self._pick_first(
            payload,
            [
                "request_id",
                "requestId",
                "client_request_id",
                "clientRequestId",
                "idempotency_key",
                "idempotencyKey",
                "upload_request_id",
                "uploadRequestId",
            ],
        )
        return str(value).strip() if value else False

    def _handle_uploaded_files(self, evidence):
        uploaded = []
        files = []
        image_model = request.env["logistics.trace.evidence.image"].sudo()
        for key in request.httprequest.files.keys():
            files.extend(request.httprequest.files.getlist(key))
        if not files:
            return uploaded
        for index, storage_file in enumerate(files, start=1):
            content = storage_file.read()
            storage_file.stream.seek(0)
            if not content:
                continue
            content_sha256 = hashlib.sha256(content).hexdigest()
            existing_image = image_model.search(
                [
                    ("evidence_id", "=", evidence.id),
                    ("content_sha256", "=", content_sha256),
                    ("storage_status", "!=", "deleted"),
                ],
                order="id desc",
                limit=1,
            )
            image_record = existing_image or evidence.sudo().upload_image_binary(
                file_name=storage_file.filename or f"trace_{evidence.id}_{index}.jpg",
                content=content,
                content_type=storage_file.mimetype or "application/octet-stream",
                sequence=index * 10,
                content_sha256=content_sha256,
            )
            uploaded.append(
                {
                    "image_id": image_record.id,
                    "image_access_key": image_record.image_access_key,
                    "preview_url": image_record.preview_url or "",
                    "deduplicated": bool(existing_image),
                }
            )
        return uploaded

    def _normalize_trace_type(self, value):
        raw = (value or "").strip()
        if not raw:
            return "arrive_store"
        mapping = {
            "arrive": "arrive_store",
            "arrive_store": "arrive_store",
            "arrival": "arrive_store",
            "sign": "signoff",
            "signed": "signoff",
            "signoff": "signoff",
            "deliver_finish": "deliver_finish",
            "finish": "deliver_finish",
            "load": "finish_loading",
            "loading": "finish_loading",
            "load_finish": "finish_loading",
            "load_complete": "finish_loading",
            "finish_loading": "finish_loading",
            "start_loading": "start_loading",
            "load_start": "start_loading",
            "loading_start": "start_loading",
            "leave": "departed",
            "depart": "departed",
            "departed": "departed",
            "exception": "exception_report",
        }
        return mapping.get(raw, raw)

    def _build_node_id(self, waybill, customer_line):
        if not customer_line:
            return f"{waybill.name}:{waybill.route_seq or 0}"
        line_no = customer_line.customer_line_no or str(customer_line.id)
        return f"{waybill.name}:{line_no}"

    def _pick_first(self, payload, keys):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                value = value[0] if value else False
            if value not in (None, "", False):
                return value
        return False

    def _coerce_int(self, value):
        if value in (None, "", False):
            return None
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            return None

    def _json_response(self, payload, *, status):
        return request.make_response(
            json.dumps(payload, ensure_ascii=False),
            headers=[("Content-Type", "application/json")],
            status=status,
        )
