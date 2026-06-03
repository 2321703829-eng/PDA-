import base64
import io
import json
import zipfile
from urllib.parse import quote

from odoo import fields, http
from odoo.exceptions import UserError
from odoo.http import request

from ..services.image_storage_service import LogisticsEvidenceImageStorage
from .image_capability_controller import LogisticsImageCapabilityController


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
            trace_time = payload.get("trace_time") or payload.get("occurred_at")

            values = {
                "event_type": event_type,
                "submit_source": "mobile",
                "remark": payload.get("remark"),
                "driver_name": payload.get("driver_name"),
                "plate_no": payload.get("vehicle_no") or payload.get("plate_no"),
                "location_text": payload.get("location_text"),
                "route_sequence": payload.get("route_sequence"),
                "source_channel": payload.get("source_channel") or "mini",
                "source_record_id": payload.get("source_record_id"),
                "is_exception": event_type == "exception_report",
            }
            if trace_time:
                values["trace_time"] = trace_time

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
            legacy_payload = self._build_legacy_waybill_stops_payload(waybill_no)
            if not legacy_payload:
                return self._json_response({"ok": False, "message": "Waybill not found."}, status=404)
            return self._json_response({"ok": True, "data": legacy_payload}, status=200)

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
        ["/api/mini/logistics/waybills/<string:waybill_no>/stops/<int:stop_seq>/evidences"],
        type="http",
        auth="user",
        methods=["DELETE"],
        csrf=False,
    )
    def delete_stop_evidences(self, waybill_no, stop_seq, **kwargs):
        waybill = self._find_waybill({"waybill_no": waybill_no})
        if not waybill:
            return self._json_response({"ok": False, "message": "Waybill not found."}, status=404)

        stop_records = request.env["logistics.dispatch.waybill.stop"].sudo().search(
            [("waybill_id", "=", waybill.id)],
            order="stop_seq asc, id asc",
        )
        if not stop_records:
            return self._json_response({"ok": False, "message": "Waybill stops not found."}, status=404)

        traces = self._search_waybill_traces(waybill)
        matched_traces = traces.filtered(
            lambda trace: self._resolve_trace_stop_seq(trace, stop_records) == stop_seq
        )
        if not matched_traces:
            return self._json_response(
                {"ok": False, "message": "No trace evidences found for the stop."},
                status=404,
            )

        evidence_model = request.env["logistics.trace.evidence"].sudo()
        evidences = evidence_model.search([("trace_event_id", "in", matched_traces.ids)])
        deleted_count = len(evidences)
        if evidences:
            evidences.unlink()

        refreshed_traces = self._search_waybill_traces(waybill)
        payload = self._build_waybill_stops_payload(waybill, stop_records, refreshed_traces)
        return self._json_response(
            {
                "ok": True,
                "message": "Stop evidences deleted successfully.",
                "data": {
                    "waybill_id": waybill.id,
                    "waybill_no": waybill.name,
                    "stop_seq": stop_seq,
                    "deleted_count": deleted_count,
                    "stops": payload["stops"],
                },
            },
            status=200,
        )

    @http.route(
        ["/logistics_trace/evidence-images/<string:image_access_key>"],
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def get_evidence_image(self, image_access_key, lang=None, download=False, **kwargs):
        storage = LogisticsEvidenceImageStorage(request.env)
        image_record = False
        try:
            image_record = (
                request.env["logistics.trace.evidence.image"]
                .sudo()
                .search([("image_access_key", "=", image_access_key)], limit=1)
            )
        except KeyError:
            image_record = False

        try:
            if image_record and image_record.storage_provider == "oss":
                payload = self._read_oss_image(image_record, download=True)
            elif image_record:
                payload = storage.read_image(image_record)
            else:
                evidence = (
                    request.env["logistics.trace.evidence"]
                    .sudo()
                    .search([("image_access_key", "=", image_access_key)], limit=1)
                )
                if not evidence:
                    return request.not_found()
                attachment = (
                    request.env["ir.attachment"]
                    .sudo()
                    .search(
                        [
                            ("res_model", "=", "logistics.trace.evidence"),
                            ("res_id", "=", evidence.id),
                            ("description", "=", image_access_key),
                        ],
                        limit=1,
                    )
                )
                if attachment and attachment.datas:
                    content = base64.b64decode(attachment.datas)
                    payload = {
                        "file_name": attachment.name or image_access_key,
                        "content_type": attachment.mimetype or "application/octet-stream",
                        "content_length": len(content),
                        "content": content,
                    }
                else:
                    payload = storage.read_legacy_image(
                        evidence.name or image_access_key,
                        evidence.full_url,
                        evidence.preview_url,
                    )
        except UserError:
            return request.not_found()

        disposition = "attachment" if download else "inline"
        encoded_name = quote(payload["file_name"])
        headers = [
            ("Content-Type", payload["content_type"]),
            ("Content-Length", str(payload["content_length"])),
            ("Content-Disposition", f"{disposition}; filename*=UTF-8''{encoded_name}"),
        ]
        return request.make_response(payload["content"], headers=headers)

    @http.route(
        [
            "/logistics_trace/waybills/<int:waybill_id>/evidences/download",
            "/<string:lang>/logistics_trace/waybills/<int:waybill_id>/evidences/download",
        ],
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def download_waybill_evidence_images(self, waybill_id, lang=None, upload_role=None, **kwargs):
        domain = [("waybill_id", "=", waybill_id), ("state", "!=", "missing")]
        if upload_role:
            domain.append(("upload_role", "=", upload_role))

        evidences = (
            request.env["logistics.trace.evidence"]
            .sudo()
            .search(domain, order="uploaded_at desc, sequence asc, id asc")
        )
        if not evidences:
            return request.not_found()

        storage = LogisticsEvidenceImageStorage(request.env)
        zip_entries = []
        used_names = set()
        for evidence in evidences:
            image_records = evidence.image_ids.filtered(
                lambda rec: rec.storage_status != "deleted"
            ).sorted(key=lambda rec: (rec.sequence, rec.id))
            if image_records:
                for image in image_records:
                    try:
                        if image.storage_provider == "oss":
                            payload = self._read_oss_image(image, download=True)
                        else:
                            payload = storage.read_image(image)
                    except UserError:
                        continue
                    archive_name = self._unique_archive_name(
                        payload.get("file_name") or image.image_access_key or "evidence-image",
                        used_names,
                    )
                    zip_entries.append((archive_name, payload["content"]))
            elif evidence.image_access_key or evidence.full_url or evidence.preview_url:
                try:
                    payload = self._read_legacy_evidence_payload(storage, evidence)
                except UserError:
                    continue
                archive_name = self._unique_archive_name(
                    payload.get("file_name") or evidence.image_access_key or evidence.name or "evidence-image",
                    used_names,
                )
                zip_entries.append((archive_name, payload["content"]))

        if not zip_entries:
            return request.not_found()

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            for archive_name, content in zip_entries:
                archive.writestr(archive_name, content)
        content = buffer.getvalue()

        waybill = request.env["logistics.dispatch.waybill"].sudo().browse(waybill_id)
        file_name = "%s-evidence-images.zip" % (waybill.name or ("waybill-%s" % waybill_id))
        encoded_name = quote(file_name)
        headers = [
            ("Content-Type", "application/zip"),
            ("Content-Length", str(len(content))),
            ("Content-Disposition", f"attachment; filename*=UTF-8''{encoded_name}"),
        ]
        return request.make_response(content, headers=headers)

    def _read_oss_image(self, image_record, *, download):
        signer = LogisticsImageCapabilityController()
        config = request.env["ir.config_parameter"].sudo()
        session = {
            "image_access_key": image_record.image_access_key,
            "bucket": image_record.storage_bucket or (config.get_param("logistics_trace_image_accel.bucket", default="") or "").strip(),
            "endpoint": (config.get_param("logistics_trace_image_accel.endpoint", default="") or "").strip(),
            "object_key": image_record.storage_relative_path or "",
            "mime_type": image_record.mime_type or "image/jpeg",
            "filename": image_record.source_filename or image_record.stored_file_name or image_record.image_access_key,
        }
        if not all([session["bucket"], session["endpoint"], session["object_key"]]):
            raise UserError("OSS image metadata is incomplete.")
        signed_url = signer._build_signed_oss_url(config, session, method="GET")
        if not download:
            return {"url": signed_url}
        result = signer._download_oss_object(config, session)
        if not result.get("ok"):
            raise UserError(result.get("message") or "OSS image download failed.")
        content = result.get("content") or b""
        result.update(
            {
                "file_name": session["filename"],
                "content_type": result.get("mime_type") or session["mime_type"],
                "content_length": len(content),
            }
        )
        return result

    def _read_legacy_evidence_payload(self, storage, evidence):
        attachment = (
            request.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "logistics.trace.evidence"),
                    ("res_id", "=", evidence.id),
                    ("description", "=", evidence.image_access_key),
                ],
                limit=1,
            )
        )
        if attachment and attachment.datas:
            content = base64.b64decode(attachment.datas)
            return {
                "file_name": attachment.name or evidence.image_access_key,
                "content_type": attachment.mimetype or "application/octet-stream",
                "content_length": len(content),
                "content": content,
            }
        return storage.read_legacy_image(
            evidence.name or evidence.image_access_key or "evidence-image",
            evidence.full_url,
            evidence.preview_url,
        )

    def _unique_archive_name(self, file_name, used_names):
        safe_name = (file_name or "evidence-image").strip().replace("/", "_").replace("\\", "_")
        if not safe_name:
            safe_name = "evidence-image"
        candidate = safe_name
        index = 2
        while candidate in used_names:
            if "." in safe_name:
                stem, ext = safe_name.rsplit(".", 1)
                candidate = f"{stem}-{index}.{ext}"
            else:
                candidate = f"{safe_name}-{index}"
            index += 1
        used_names.add(candidate)
        return candidate

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
        evidence_by_trace = self._build_evidence_map(traces)
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
                "evidence_images": [],
            }
            stops.append(stop)
            stop_index[stop_record.stop_seq] = stop

        for trace in traces:
            stop_seq = self._resolve_trace_stop_seq(trace, stop_records)
            stop = stop_index.get(stop_seq)
            if not stop:
                continue
            self._merge_trace_into_stop(stop, trace, evidence_by_trace.get(trace.id, []))

        return {
            "waybill_id": waybill.id,
            "waybill_no": waybill.name,
            "batch_id": waybill.batch_id.id if waybill.batch_id else False,
            "batch_no": waybill.batch_id.name if waybill.batch_id else False,
            "driver_name": waybill.driver_employee_id.name if waybill.driver_employee_id else False,
            "vehicle_no": waybill.vehicle_id.license_plate if waybill.vehicle_id else False,
            "stops": stops,
        }

    def _build_legacy_waybill_stops_payload(self, waybill_no):
        legacy_rows = self._fetch_legacy_waybill_stop_rows(waybill_no)
        if not legacy_rows:
            return None

        first_row = legacy_rows[0]
        legacy_traces = self._search_legacy_waybill_traces(waybill_no)
        legacy_evidence_map = self._build_legacy_evidence_map(legacy_traces)
        stops = []
        stop_index = {}
        for node_id, row in enumerate(legacy_rows, start=1):
            contact_list = self._load_legacy_contact_list(row)
            primary_contact = contact_list[0] if contact_list else {"name": None, "phone": None}
            stop = {
                "node_id": node_id,
                "stop_seq": row.get("stop_seq") or node_id,
                "store_name": row.get("store_name"),
                "address": row.get("address"),
                "lat": row.get("lat"),
                "lng": row.get("lng"),
                "contact_name": primary_contact.get("name"),
                "contact_phone": primary_contact.get("phone"),
                "contact_list": contact_list,
                "guide_url": row.get("guide_url"),
                "goods_info": row.get("goods_info") or "",
                "status": "PENDING",
                "evidence_images": [],
            }
            stops.append(stop)
            stop_index[stop["stop_seq"]] = stop

        for trace in legacy_traces:
            stop = stop_index.get(trace.route_sequence or 0)
            if not stop:
                continue
            self._merge_trace_into_stop(stop, trace, legacy_evidence_map.get(trace.id, []))

        return {
            "waybill_id": False,
            "waybill_no": waybill_no,
            "batch_id": False,
            "batch_no": first_row.get("batch_no") or False,
            "driver_name": first_row.get("driver_name") or False,
            "vehicle_no": first_row.get("vehicle_no") or False,
            "stops": stops,
        }

    @staticmethod
    def _fetch_legacy_waybill_stop_rows(waybill_no):
        cr = request.env.cr
        cr.execute("SELECT to_regclass('public.logistics_waybill_stop')")
        if not cr.fetchone()[0]:
            return []

        cr.execute(
            """
            SELECT
                id,
                waybill_no,
                batch_no,
                stop_seq,
                store_name,
                address,
                contact_name,
                contact_phone,
                guide_url,
                driver_name,
                vehicle_no,
                contact_list_json,
                goods_info,
                lat,
                lng
            FROM logistics_waybill_stop
            WHERE waybill_no = %s
            ORDER BY stop_seq ASC, id ASC
            """,
            [waybill_no],
        )
        return cr.dictfetchall()

    @staticmethod
    def _search_legacy_waybill_traces(waybill_no):
        return request.env["logistics.trace.event"].sudo().search(
            [
                ("object_type", "=", "waybill"),
                ("waybill_id", "=", False),
                ("source_record_id", "=", waybill_no),
            ],
            order="route_sequence asc, trace_time asc, id asc",
        )

    @staticmethod
    def _resolve_trace_stop_seq(trace, stop_records):
        stop_seq = trace.route_sequence or 0
        if not stop_seq and len(stop_records) == 1:
            stop_seq = stop_records[0].stop_seq
        return stop_seq

    def _build_evidence_map(self, traces):
        evidence_map = {}
        if not traces:
            return evidence_map

        evidences = request.env["logistics.trace.evidence"].sudo().search(
            [("trace_event_id", "in", traces.ids)],
            order="uploaded_at asc, id asc",
        )
        for evidence in evidences:
            evidence_map.setdefault(evidence.trace_event_id.id, []).append(
                {
                    "evidence_id": evidence.id,
                    "image_access_key": evidence.image_access_key,
                    "preview_url": evidence.preview_url,
                    "full_url": evidence.full_url,
                    "state": evidence.state,
                    "uploaded_at": (
                        fields.Datetime.to_string(evidence.uploaded_at) if evidence.uploaded_at else False
                    ),
                    "uploader_name": evidence.uploader_name,
                }
            )
        return evidence_map

    def _build_legacy_evidence_map(self, traces):
        evidence_map = {}
        if not traces:
            return evidence_map

        evidences = request.env["logistics.trace.evidence"].sudo().search(
            [("trace_event_id", "in", traces.ids)],
            order="id asc",
        )
        if not evidences:
            return evidence_map

        evidence_by_id = {evidence.id: evidence for evidence in evidences}
        cr = request.env.cr
        cr.execute("SELECT to_regclass('public.logistics_trace_evidence_image')")
        if not cr.fetchone()[0]:
            return evidence_map

        cr.execute(
            """
            SELECT
                id,
                evidence_id,
                image_access_key,
                source_filename,
                stored_file_name,
                storage_status
            FROM logistics_trace_evidence_image
            WHERE evidence_id = ANY(%s)
            ORDER BY id ASC
            """,
            [list(evidence_by_id)],
        )
        base_url = request.httprequest.host_url.rstrip("/")
        for row in cr.dictfetchall():
            evidence = evidence_by_id.get(row["evidence_id"])
            if not evidence or not row.get("image_access_key"):
                continue
            image_access_key = row["image_access_key"]
            preview_url = f"{base_url}/logistics_trace/evidence-images/{image_access_key}"
            evidence_map.setdefault(evidence.trace_event_id.id, []).append(
                {
                    "evidence_id": evidence.id,
                    "image_access_key": image_access_key,
                    "preview_url": preview_url,
                    "full_url": preview_url,
                    "state": evidence.state,
                    "uploaded_at": (
                        fields.Datetime.to_string(evidence.uploaded_at) if evidence.uploaded_at else False
                    ),
                    "uploader_name": evidence.uploader_name,
                    "file_name": row.get("source_filename") or row.get("stored_file_name"),
                    "storage_status": row.get("storage_status"),
                }
            )
        return evidence_map

    def _merge_trace_into_stop(self, stop, trace, evidences):
        stop["status"] = self._merge_stop_status(stop["status"], trace.event_type, trace.is_exception)
        if evidences:
            stop["evidence_images"] = evidences

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
    def _load_legacy_contact_list(stop_row):
        raw_json = stop_row.get("contact_list_json")
        if raw_json:
            try:
                contact_list = json.loads(raw_json)
                if isinstance(contact_list, list):
                    return contact_list[:3]
            except json.JSONDecodeError:
                pass
        if stop_row.get("contact_name") or stop_row.get("contact_phone"):
            return [
                {
                    "name": stop_row.get("contact_name") or "",
                    "phone": stop_row.get("contact_phone") or "",
                }
            ]
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
