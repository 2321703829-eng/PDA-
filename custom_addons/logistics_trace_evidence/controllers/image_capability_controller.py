import base64
import hmac
import json
import urllib.error
import urllib.parse
import urllib.request
from email.utils import formatdate
from datetime import datetime, timedelta, timezone
from hashlib import sha1
from pathlib import Path
from secrets import token_hex

from odoo import http
from odoo.http import request
from odoo.tools import config as odoo_config


class LogisticsImageCapabilityController(http.Controller):
    _MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}

    @http.route(
        ["/api/mini/logistics/images/capability"],
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def image_capability(self, **kwargs):
        config = self._config()
        enabled = self._is_enabled(config.get_param("logistics_trace_image_accel.enabled", default="0"))
        allowed = enabled and self._is_user_allowed(config)
        max_upload_mb = self._int_param(config, "logistics_trace_image_accel.max_upload_mb", 10, minimum=1)
        payload = {
            "ok": True,
            "data": {
                "image_accel_enabled": allowed,
                "upload_mode": "cloud_direct_upload" if allowed else "multipart_to_odoo",
                "max_upload_bytes": max_upload_mb * 1024 * 1024,
                "accept_mime_types": ["image/jpeg", "image/png", "image/webp", "image/bmp"],
            },
        }
        return self._json_response(payload, status=200)

    @http.route(
        ["/api/mini/logistics/images/init-upload"],
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def init_upload(self, **kwargs):
        config = self._config()
        if not self._is_enabled(config.get_param("logistics_trace_image_accel.enabled", default="0")):
            return self._json_response({"ok": False, "message": "Image acceleration is disabled."}, status=409)
        if not self._is_user_allowed(config):
            return self._json_response({"ok": False, "message": "Image acceleration is not enabled for this user."}, status=403)

        payload = request.httprequest.get_json(silent=True) or {}
        filename = (payload.get("filename") or "").strip()
        mime_type = (payload.get("mime_type") or "").strip().lower()
        try:
            file_size = int(payload.get("file_size") or 0)
        except (TypeError, ValueError):
            file_size = 0
        business_ref = payload.get("business_ref") or {}
        upload_role = self._resolve_upload_role(payload, business_ref)

        error = self._validate_init_payload(config, filename, mime_type, file_size, business_ref)
        if error:
            return self._json_response({"ok": False, "message": error}, status=400)

        provider = (config.get_param("logistics_trace_image_accel.provider", default="") or "").strip()
        if provider != "aliyun_oss":
            return self._json_response({"ok": False, "message": "OSS provider is not configured."}, status=501)

        bucket = (config.get_param("logistics_trace_image_accel.bucket", default="") or "").strip()
        endpoint = (config.get_param("logistics_trace_image_accel.endpoint", default="") or "").strip()
        access_key_id = (config.get_param("logistics_trace_image_accel.access_key_id", default="") or "").strip()
        access_key_secret = (config.get_param("logistics_trace_image_accel.access_key_secret", default="") or "").strip()
        if not all([bucket, endpoint, access_key_id, access_key_secret]):
            return self._json_response({"ok": False, "message": "OSS credential or bucket config is missing."}, status=500)

        ttl = self._int_param(config, "logistics_trace_image_accel.upload_url_ttl_seconds", 600, minimum=60)
        max_bytes = self._int_param(config, "logistics_trace_image_accel.max_upload_mb", 10, minimum=1) * 1024 * 1024
        expire_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        image_access_key = f"img_{token_hex(16)}"
        object_key = self._build_object_key(image_access_key, filename)
        policy = self._build_post_policy(expire_at, object_key, mime_type, max_bytes)
        policy_b64 = base64.b64encode(json.dumps(policy, separators=(",", ":")).encode()).decode()
        signature = base64.b64encode(hmac.new(access_key_secret.encode(), policy_b64.encode(), sha1).digest()).decode()
        upload_url = f"https://{bucket}.{endpoint}"
        form_fields = {
            "key": object_key,
            "policy": policy_b64,
            "OSSAccessKeyId": access_key_id,
            "Signature": signature,
            "success_action_status": "200",
            "Content-Type": mime_type,
        }
        session = {
            "image_access_key": image_access_key,
            "filename": filename,
            "mime_type": mime_type,
            "file_size": file_size,
            "business_ref": business_ref,
            "upload_role": upload_role,
            "provider": provider,
            "bucket": bucket,
            "endpoint": endpoint,
            "object_key": object_key,
            "upload_method": "POST_FORM",
            "expire_at": expire_at.isoformat(),
            "storage_status": "cloud_only",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": request.env.user.id,
        }
        config.set_param(f"logistics_trace_image_accel.session.{image_access_key}", json.dumps(session, ensure_ascii=False))
        return self._json_response(
            {
                "ok": True,
                "data": {
                    "image_access_key": image_access_key,
                    "upload_mode": "cloud_direct_upload",
                    "upload_method": "POST_FORM",
                    "upload_url": upload_url,
                    "form_fields": form_fields,
                    "headers": None,
                    "expire_at": expire_at.isoformat(),
                    "storage_status": "cloud_only",
                },
            },
            status=200,
        )


    @http.route(
        ["/api/mini/logistics/images/complete-upload"],
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def complete_upload(self, **kwargs):
        config = self._config()
        if not self._is_enabled(config.get_param("logistics_trace_image_accel.enabled", default="0")):
            return self._json_response({"ok": False, "message": "Image acceleration is disabled."}, status=409)
        if not self._is_user_allowed(config):
            return self._json_response({"ok": False, "message": "Image acceleration is not enabled for this user."}, status=403)

        payload = request.httprequest.get_json(silent=True) or {}
        image_access_key = (payload.get("image_access_key") or "").strip()
        if not image_access_key:
            return self._json_response({"ok": False, "message": "image_access_key is required."}, status=400)

        session = self._load_session(config, image_access_key)
        if not session:
            return self._json_response({"ok": False, "message": "upload session not found."}, status=404)
        if session.get("created_by") and session.get("created_by") != request.env.user.id:
            return self._json_response({"ok": False, "message": "upload session does not belong to current user."}, status=403)
        upload_role = self._resolve_upload_role(payload, session.get("business_ref") or {})
        if upload_role != "unknown":
            session["upload_role"] = upload_role

        oss_meta = self._head_oss_object(config, session)
        if not oss_meta.get("ok"):
            return self._json_response({"ok": False, "message": oss_meta.get("message") or "OSS object check failed."}, status=oss_meta.get("status") or 502)

        evidence_result = self._write_evidence_record(config, session, oss_meta)
        if not evidence_result.get("ok"):
            return self._json_response({"ok": False, "message": evidence_result.get("message")}, status=evidence_result.get("status") or 400)

        session["storage_status"] = "cloud_only"
        session["completed_at"] = datetime.now(timezone.utc).isoformat()
        session["evidence_id"] = evidence_result["evidence"].id
        session["oss_etag"] = oss_meta.get("etag")
        session["oss_size"] = oss_meta.get("file_size")
        config.set_param(f"logistics_trace_image_accel.session.{image_access_key}", json.dumps(session, ensure_ascii=False))

        preview_url = self._build_signed_oss_url(config, session, method="GET")
        return self._json_response(
            {
                "ok": True,
                "data": {
                    "image_access_key": image_access_key,
                    "evidence_id": evidence_result["evidence"].id,
                    "storage_status": "cloud_only",
                    "preview_url": preview_url,
                    "preview_expires_at": self._signed_url_expire_at(config).isoformat(),
                },
            },
            status=200,
        )

    @http.route(
        ["/api/mini/logistics/images/<string:image_access_key>/preview-url"],
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def preview_url(self, image_access_key, **kwargs):
        config = self._config()
        session = self._load_session(config, image_access_key)
        if not session:
            return self._json_response({"ok": False, "message": "image_access_key not found."}, status=404)
        if session.get("created_by") and session.get("created_by") != request.env.user.id:
            return self._json_response({"ok": False, "message": "image_access_key does not belong to current user."}, status=403)
        local_url = self._build_local_preview_url(config, session)
        if local_url and self._local_file_exists(config, session):
            return self._json_response(
                {
                    "ok": True,
                    "data": {
                        "image_access_key": image_access_key,
                        "storage_status": session.get("storage_status") or "both",
                        "selected_storage": "local",
                        "url": local_url,
                        "expires_at": None,
                    },
                },
                status=200,
            )
        expire_at = self._signed_url_expire_at(config)
        return self._json_response(
            {
                "ok": True,
                "data": {
                    "image_access_key": image_access_key,
                    "storage_status": session.get("storage_status") or "cloud_only",
                    "selected_storage": "cloud",
                    "url": self._build_signed_oss_url(config, session, method="GET", expire_at=expire_at),
                    "expires_at": expire_at.isoformat(),
                },
            },
            status=200,
        )

    @http.route(
        ["/api/mini/logistics/images/archive-one"],
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def archive_one(self, **kwargs):
        config = self._config()
        if not self._is_enabled(config.get_param("logistics_trace_image_accel.enabled", default="0")):
            return self._json_response({"ok": False, "message": "Image acceleration is disabled."}, status=409)
        if not request.env.user.has_group("base.group_system"):
            return self._json_response({"ok": False, "message": "archive-one is an operations-only endpoint."}, status=403)

        payload = request.httprequest.get_json(silent=True) or {}
        image_access_key = (payload.get("image_access_key") or "").strip()
        if not image_access_key:
            return self._json_response({"ok": False, "message": "image_access_key is required."}, status=400)

        session = self._load_session(config, image_access_key)
        if not session:
            return self._json_response({"ok": False, "message": "upload session not found."}, status=404)
        if session.get("created_by") and session.get("created_by") != request.env.user.id:
            return self._json_response({"ok": False, "message": "upload session does not belong to current user."}, status=403)

        result = self._archive_session_to_local(config, session)
        if not result.get("ok"):
            return self._json_response({"ok": False, "message": result.get("message")}, status=result.get("status") or 500)

        return self._json_response(
            {
                "ok": True,
                "data": {
                    "image_access_key": image_access_key,
                    "evidence_id": result["evidence"].id,
                    "storage_status": session.get("storage_status"),
                    "selected_storage": "local",
                    "preview_url": self._build_local_preview_url(config, session),
                    "local_relative_path": session.get("local_relative_path"),
                    "cloud_object_key": session.get("object_key"),
                },
            },
            status=200,
        )


    def _load_session(self, config, image_access_key):
        raw = config.get_param(f"logistics_trace_image_accel.session.{image_access_key}", default="") or ""
        if not raw:
            return None
        try:
            return json.loads(raw)
        except ValueError:
            return None

    def _head_oss_object(self, config, session):
        bucket = session.get("bucket") or (config.get_param("logistics_trace_image_accel.bucket", default="") or "").strip()
        endpoint = session.get("endpoint") or (config.get_param("logistics_trace_image_accel.endpoint", default="") or "").strip()
        object_key = session.get("object_key") or ""
        if not all([bucket, endpoint, object_key]):
            return {"ok": False, "status": 500, "message": "OSS object session is incomplete."}
        url = f"https://{bucket}.{endpoint}/{urllib.parse.quote(object_key)}"
        date_header = formatdate(usegmt=True)
        authorization = self._oss_authorization(config, "HEAD", bucket, object_key, date_header=date_header)
        req = urllib.request.Request(url, method="HEAD", headers={"Date": date_header, "Authorization": authorization})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                return {
                    "ok": True,
                    "file_size": int(resp.headers.get("Content-Length") or session.get("file_size") or 0),
                    "mime_type": resp.headers.get("Content-Type") or session.get("mime_type"),
                    "etag": (resp.headers.get("ETag") or "").strip('"'),
                }
        except urllib.error.HTTPError as exc:
            status = 404 if exc.code == 404 else 502
            return {"ok": False, "status": status, "message": f"OSS object check failed with HTTP {exc.code}."}
        except Exception as exc:
            return {"ok": False, "status": 502, "message": f"OSS object check failed: {exc}"}

    def _write_evidence_record(self, config, session, oss_meta):
        business_ref = session.get("business_ref") or {}
        upload_role = session.get("upload_role") or "unknown"
        evidence_model = request.env["logistics.trace.evidence"].sudo()
        image_model = request.env["logistics.trace.evidence.image"].sudo()
        image_access_key = session["image_access_key"]
        existing_image = image_model.search([("image_access_key", "=", image_access_key)], limit=1)
        if existing_image:
            return {"ok": True, "evidence": existing_image.evidence_id}

        evidence = False
        evidence_id = self._safe_int(business_ref.get("evidence_id"))
        if evidence_id:
            evidence = evidence_model.browse(evidence_id).exists()
            if not evidence:
                return {"ok": False, "status": 404, "message": "evidence_id not found."}
        else:
            trace = self._resolve_trace_event(business_ref)
            if not trace:
                return {"ok": False, "status": 400, "message": "trace_event_id or evidence_id is required."}
            evidence = evidence_model.create(
                self._filter_fields(
                    evidence_model,
                    {
                        "name": "Evidence - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "trace_event_id": trace.id,
                        "uploader_id": request.env.user.id,
                        "upload_role": upload_role,
                        "state": "available",
                        "uploaded_at": datetime.now(timezone.utc).replace(tzinfo=None),
                    },
                )
            )

        filename = session.get("filename") or session.get("object_key", "").rsplit("/", 1)[-1]
        object_name = session.get("object_key", "").rsplit("/", 1)[-1]
        image_record = image_model.create(
            self._filter_fields(
                image_model,
                {
                    "evidence_id": evidence.id,
                    "sequence": 10,
                    "image_access_key": image_access_key,
                    "source_filename": filename,
                    "stored_file_name": object_name or filename,
                    "file_ext": Path(filename).suffix.lower(),
                    "mime_type": oss_meta.get("mime_type") or session.get("mime_type"),
                    "file_size": oss_meta.get("file_size") or session.get("file_size"),
                    "storage_provider": "oss",
                    "storage_bucket": session.get("bucket"),
                    "storage_relative_path": session.get("object_key"),
                    "storage_status": "active",
                    "captured_at": datetime.now(timezone.utc).replace(tzinfo=None),
                },
            )
        )
        cover_vals = self._filter_fields(
            evidence_model,
            {
                "image_access_key": image_access_key,
                "preview_url": image_record.preview_url,
                "full_url": image_record.full_url,
                "uploaded_at": datetime.now(timezone.utc).replace(tzinfo=None),
                "uploader_id": request.env.user.id,
                "upload_role": upload_role,
                "state": "available",
            },
        )
        if cover_vals:
            evidence.write(cover_vals)
        return {"ok": True, "evidence": evidence}

    def _resolve_trace_event(self, business_ref):
        trace_event_id = self._safe_int(business_ref.get("trace_event_id"))
        if trace_event_id:
            trace = request.env["logistics.trace.event"].sudo().browse(trace_event_id).exists()
            if trace:
                return trace
        customer_line_id = self._safe_int(business_ref.get("customer_line_id"))
        if customer_line_id:
            try:
                line = request.env["logistics.dispatch.waybill.customer.goods.line"].sudo().browse(customer_line_id).exists()
            except KeyError:
                line = False
            waybill = line.waybill_id if line and "waybill_id" in line._fields else False
            if waybill:
                return request.env["logistics.trace.event"].sudo().search(
                    [("waybill_id", "=", waybill.id)],
                    order="trace_time desc, id desc",
                    limit=1,
                )
        return False

    @staticmethod
    def _filter_fields(model, values):
        return {key: value for key, value in values.items() if key in model._fields}

    @staticmethod
    def _safe_int(value):
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _resolve_upload_role(payload, business_ref=None):
        business_ref = business_ref or {}
        raw_role = (
            payload.get("upload_role")
            or payload.get("uploader_role")
            or payload.get("operator_role")
            or payload.get("source_role")
            or payload.get("identity")
            or business_ref.get("upload_role")
            or business_ref.get("uploader_role")
            or business_ref.get("operator_role")
            or business_ref.get("source_role")
            or business_ref.get("identity")
            or ""
        )
        normalized_role = str(raw_role).strip().lower()
        warehouse_values = {
            "warehouse",
            "warehouse_user",
            "warehouse_operator",
            "mini_warehouse",
            "storehouse",
            "stock",
            "仓库",
            "仓库端",
            "仓库身份",
        }
        driver_values = {
            "driver",
            "driver_user",
            "driver_operator",
            "mini_driver",
            "司机",
            "司机端",
            "司机身份",
        }
        if normalized_role in warehouse_values:
            return "warehouse"
        if normalized_role in driver_values:
            return "driver"
        return "unknown"

    def _archive_session_to_local(self, config, session):
        image_access_key = session.get("image_access_key")
        evidence = request.env["logistics.trace.evidence"].sudo().search([("image_access_key", "=", image_access_key)], limit=1)
        if not evidence:
            return {"ok": False, "status": 404, "message": "evidence record not found; call complete-upload first."}

        content_result = self._download_oss_object(config, session)
        if not content_result.get("ok"):
            return content_result

        local_relative_path = session.get("local_relative_path") or self._build_local_relative_path(session)
        root = self._get_local_storage_root(config)
        target = root / local_relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content_result["content"])

        local_url = self._build_local_preview_url(config, {**session, "local_relative_path": local_relative_path})
        evidence.write(
            {
                "preview_url": local_url,
                "full_url": local_url,
                "stored_file_name": target.name,
                "file_ext": target.suffix.lower(),
                "mime_type": content_result.get("mime_type") or session.get("mime_type"),
                "file_size": len(content_result["content"]),
                "storage_provider": "local",
                "storage_bucket": False,
                "storage_relative_path": local_relative_path,
                "state": "available",
            }
        )
        session["storage_status"] = "both"
        session["local_relative_path"] = local_relative_path
        session["local_synced_at"] = datetime.now(timezone.utc).isoformat()
        config.set_param(f"logistics_trace_image_accel.session.{image_access_key}", json.dumps(session, ensure_ascii=False))
        return {"ok": True, "evidence": evidence}

    def _download_oss_object(self, config, session):
        url = self._build_signed_oss_url(config, session, method="GET")
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                return {
                    "ok": True,
                    "content": resp.read(),
                    "mime_type": resp.headers.get("Content-Type") or session.get("mime_type"),
                }
        except urllib.error.HTTPError as exc:
            return {"ok": False, "status": 502, "message": f"OSS object download failed with HTTP {exc.code}."}
        except Exception as exc:
            return {"ok": False, "status": 502, "message": f"OSS object download failed: {exc}"}

    def _get_local_storage_root(self, config):
        root = (config.get_param("logistics_trace_evidence.image_storage_root", default="") or "").strip()
        if root:
            return Path(root)
        data_dir = odoo_config.get("data_dir")
        if data_dir:
            return Path(data_dir) / "logistics_trace_images"
        return Path.home() / ".local" / "share" / "Odoo" / "logistics_trace_images"

    def _build_local_relative_path(self, session):
        filename = session.get("filename") or session.get("object_key", "").rsplit("/", 1)[-1]
        ext = Path(filename).suffix.lower() or ".bin"
        today = datetime.now().strftime("%Y/%m/%d")
        return f"{today}/{session['image_access_key']}{ext}"

    def _build_local_preview_url(self, config, session):
        if not session.get("local_relative_path"):
            return False
        return f"/logistics_trace/evidence-images/{session['image_access_key']}"

    def _local_file_exists(self, config, session):
        relative_path = session.get("local_relative_path")
        if not relative_path:
            return False
        return (self._get_local_storage_root(config) / relative_path).exists()

    def _signed_url_expire_at(self, config):
        ttl = self._int_param(config, "logistics_trace_image_accel.preview_url_ttl_seconds", 600, minimum=60)
        return datetime.now(timezone.utc) + timedelta(seconds=ttl)

    def _build_signed_oss_url(self, config, session, *, method, expire_at=None):
        bucket = session.get("bucket") or (config.get_param("logistics_trace_image_accel.bucket", default="") or "").strip()
        endpoint = session.get("endpoint") or (config.get_param("logistics_trace_image_accel.endpoint", default="") or "").strip()
        object_key = session.get("object_key") or ""
        expire_at = expire_at or self._signed_url_expire_at(config)
        expires = str(int(expire_at.timestamp()))
        signature = self._oss_signature(config, method, bucket, object_key, expires=expires)
        query = urllib.parse.urlencode({
            "OSSAccessKeyId": (config.get_param("logistics_trace_image_accel.access_key_id", default="") or "").strip(),
            "Expires": expires,
            "Signature": signature,
        })
        return f"https://{bucket}.{endpoint}/{urllib.parse.quote(object_key)}?{query}"

    def _oss_authorization(self, config, method, bucket, object_key, *, date_header):
        access_key_id = (config.get_param("logistics_trace_image_accel.access_key_id", default="") or "").strip()
        signature = self._oss_signature(config, method, bucket, object_key, date_header=date_header)
        return f"OSS {access_key_id}:{signature}"

    def _oss_signature(self, config, method, bucket, object_key, *, date_header="", expires=""):
        access_key_secret = (config.get_param("logistics_trace_image_accel.access_key_secret", default="") or "").strip()
        date_or_expires = expires or date_header
        canonical = f"/{bucket}/{object_key}"
        string_to_sign = f"{method}\n\n\n{date_or_expires}\n{canonical}"
        return base64.b64encode(hmac.new(access_key_secret.encode(), string_to_sign.encode(), sha1).digest()).decode()

    def _validate_init_payload(self, config, filename, mime_type, file_size, business_ref):
        if not filename:
            return "filename is required."
        if mime_type not in self._MIME_TYPES:
            return "unsupported mime_type."
        max_bytes = self._int_param(config, "logistics_trace_image_accel.max_upload_mb", 10, minimum=1) * 1024 * 1024
        if file_size <= 0:
            return "file_size is required."
        if file_size > max_bytes:
            return "file_size exceeds limit."
        if not isinstance(business_ref, dict):
            return "business_ref must be an object."
        if not any(business_ref.get(key) for key in ("trace_event_id", "customer_line_id", "evidence_id")):
            return "business_ref requires trace_event_id, customer_line_id, or evidence_id."
        return None

    @staticmethod
    def _config():
        return request.env["ir.config_parameter"].sudo()

    @staticmethod
    def _json_response(payload, *, status):
        return request.make_response(
            json.dumps(payload),
            headers=[("Content-Type", "application/json")],
            status=status,
        )

    @staticmethod
    def _is_enabled(value):
        return str(value or "").strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _parse_ids(value):
        ids = set()
        for item in str(value or "").replace(";", ",").split(","):
            item = item.strip()
            if not item:
                continue
            try:
                ids.add(int(item))
            except ValueError:
                continue
        return ids

    def _is_user_allowed(self, config):
        rollout_mode = (config.get_param("logistics_trace_image_accel.rollout_mode", default="all") or "allowlist").strip().lower()
        if rollout_mode in {"all", "full", "global"}:
            return True
        if rollout_mode in {"off", "disabled", "none"}:
            return False
        user_ids = self._parse_ids(config.get_param("logistics_trace_image_accel.test_user_ids", default=""))
        return bool(user_ids and request.env.user.id in user_ids)

    @staticmethod
    def _int_param(config, key, default, *, minimum):
        try:
            value = int(config.get_param(key, default=str(default)) or default)
        except (TypeError, ValueError):
            value = default
        return max(value, minimum)

    @staticmethod
    def _build_object_key(image_access_key, filename):
        ext = Path(filename).suffix.lower() or ".bin"
        today = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        return f"mini/{today}/{image_access_key}{ext}"

    @staticmethod
    def _build_post_policy(expire_at, object_key, mime_type, max_bytes):
        return {
            "expiration": expire_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "conditions": [
                ["eq", "$key", object_key],
                ["eq", "$Content-Type", mime_type],
                ["content-length-range", 1, max_bytes],
                {"success_action_status": "200"},
            ],
        }
