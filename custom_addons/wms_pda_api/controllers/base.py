import hashlib
import json
import uuid

from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import Response, request


class WmsPdaBaseController(http.Controller):
    ERR_AUTH_FAILED = 1001
    ERR_PERMISSION = 1002
    ERR_BAD_PARAM = 2001
    ERR_NOT_FOUND = 2002
    ERR_STATE_CONFLICT = 2003
    ERR_BARCODE_UNKNOWN = 2004
    ERR_STOCK_INSUFFICIENT = 3001
    ERR_QTY_EXCEED = 3002
    ERR_TASK_LOCKED = 3003
    ERR_INTERNAL = 5000

    def _authenticate(self):
        auth_header = request.httprequest.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise AccessError("缺少或无效的 Authorization Header。")
        token_value = auth_header[7:].strip()
        token = (
            request.env["wms.api.token"]
            .sudo()
            .search([("token", "=", token_value), ("is_active", "=", True)], limit=1)
        )
        if not token or token.is_expired:
            raise AccessError("Token 已过期或无效。")
        token.touch()
        return token.user_id, token.warehouse_id, token

    def _get_payload(self):
        payload = dict(request.params)
        if request.httprequest.mimetype == "application/json":
            json_body = request.httprequest.get_json(silent=True) or {}
            if isinstance(json_body, dict):
                payload.update({key: value for key, value in json_body.items() if value is not None})
        return payload

    def _success(self, data=None, tts=""):
        body = {"code": 0, "message": "success", "data": data or {}}
        if tts:
            body["tts"] = tts
        return self._make_response(body)

    def _error(self, code, message, status=400, data=None, tts=""):
        body = {"code": code, "message": message, "data": data or {}}
        if tts:
            body["tts"] = tts
        return self._make_response(body, status=status)

    def _make_response(self, payload, *, status=200):
        return Response(
            json.dumps(payload, ensure_ascii=False, default=str),
            status=status,
            headers=[("Content-Type", "application/json; charset=utf-8")],
        )

    def _handle_request(self, callback, require_auth=True):
        try:
            if require_auth:
                user, warehouse, token = self._authenticate()
            else:
                user, warehouse, token = None, None, None
            result = callback(user, warehouse, token)
            if isinstance(result, Response):
                return result
            return self._success(result)
        except AccessError as exc:
            return self._error(self.ERR_AUTH_FAILED, str(exc), status=401)
        except ValidationError as exc:
            return self._error(self.ERR_BAD_PARAM, str(exc), status=400)
        except ValueError as exc:
            return self._error(self.ERR_BAD_PARAM, str(exc), status=400)
        except Exception as exc:
            return self._error(self.ERR_INTERNAL, str(exc), status=500)

    def _request_id(self, prefix):
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    def _handle_idempotent_request(self, payload, callback, require_auth=True):
        try:
            if require_auth:
                user, warehouse, token = self._authenticate()
            else:
                user, warehouse, token = None, None, None
            result = self._run_idempotent(payload, user, warehouse, token, lambda: callback(user, warehouse, token))
            if isinstance(result, Response):
                return result
            return self._success(result)
        except AccessError as exc:
            return self._error(self.ERR_AUTH_FAILED, str(exc), status=401)
        except ValidationError as exc:
            return self._error(self.ERR_BAD_PARAM, str(exc), status=400)
        except ValueError as exc:
            return self._error(self.ERR_BAD_PARAM, str(exc), status=400)
        except Exception as exc:
            return self._error(self.ERR_INTERNAL, str(exc), status=500)

    def _run_idempotent(self, payload, user, warehouse, token, callback, endpoint=None, method=None):
        payload = payload or {}
        request_id = (payload.get("request_id") or "").strip()
        if not request_id:
            return callback()
        endpoint = endpoint or request.httprequest.path
        method = (method or request.httprequest.method or "").upper()
        payload_hash = self._payload_hash(payload)
        device_id = (payload.get("device_id") or getattr(token, "device_id", "") or "").strip()
        Log = request.env["wms.pda.request.log"].sudo()
        log = Log.search([("request_id", "=", request_id)], limit=1)
        if log:
            if log.payload_hash != payload_hash or log.endpoint != endpoint or log.method != method:
                return self._error(self.ERR_STATE_CONFLICT, "request_id has already been used by another request.", status=409)
            if log.state == "done" and log.response_json:
                return self._make_response(self._loads_json(log.response_json))
            if log.state == "processing":
                return self._error(self.ERR_STATE_CONFLICT, "request is still processing, please retry later.", status=409)
            log.write({"state": "processing", "error_message": False, "response_json": False})
        else:
            log = Log.create(
                {
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "method": method,
                    "user_id": user.id if user else False,
                    "warehouse_id": warehouse.id if warehouse else False,
                    "device_id": device_id,
                    "payload_hash": payload_hash,
                    "state": "processing",
                }
            )
        try:
            result = callback()
            response_payload = self._response_payload(result)
            if self._response_is_success(response_payload):
                log.write({"state": "done", "response_json": self._dumps_json(response_payload), "error_message": False})
            else:
                log.write({"state": "failed", "response_json": self._dumps_json(response_payload), "error_message": response_payload.get("message")})
            return result
        except Exception as exc:
            log.write({"state": "failed", "error_message": str(exc)})
            raise

    def _payload_hash(self, payload):
        content = self._dumps_json(payload, sort_keys=True)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _response_payload(self, result):
        if isinstance(result, Response):
            return self._loads_json(result.get_data(as_text=True))
        return {"code": 0, "message": "success", "data": result or {}}

    def _response_is_success(self, payload):
        return isinstance(payload, dict) and payload.get("code") == 0

    def _dumps_json(self, payload, sort_keys=False):
        return json.dumps(payload or {}, ensure_ascii=False, default=str, sort_keys=sort_keys)

    def _loads_json(self, content):
        if isinstance(content, dict):
            return content
        if not content:
            return {}
        try:
            return json.loads(content)
        except Exception:
            return {"code": self.ERR_INTERNAL, "message": str(content), "data": {}}
