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
