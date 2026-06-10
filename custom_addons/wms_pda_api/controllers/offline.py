import re

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaOfflineSyncController(WmsPdaBaseController):
    @http.route("/api/pda/wms/v1/offline/sync", type="http", auth="public", methods=["POST"], csrf=False)
    def sync_offline_requests(self, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._sync(user, wh, token, payload))

    @http.route("/api/pda/wms/v1/offline/sync/<string:sync_id>", type="http", auth="public", methods=["GET"], csrf=False)
    def get_offline_sync(self, sync_id, **kwargs):
        return self._handle_request(lambda user, wh, token: self._get_sync(user, wh, sync_id))

    def _sync(self, user, warehouse, token, payload):
        requests_payload = payload.get("requests") or payload.get("items") or payload.get("actions") or []
        if not isinstance(requests_payload, list):
            raise ValidationError("requests must be a list.")
        sync_id = (payload.get("sync_id") or "").strip()
        Sync = request.env["wms.pda.offline.sync"].sudo()
        if sync_id:
            existing = Sync.search([("sync_id", "=", sync_id)], limit=1)
            if existing:
                if warehouse and existing.warehouse_id and existing.warehouse_id.id != warehouse.id:
                    raise ValidationError("offline sync record does not belong to current warehouse.")
                return self._format_sync(existing)
        results = []
        success_count = 0
        failed_count = 0
        for index, item in enumerate(requests_payload):
            result = self._process_item(index, item, user, warehouse, token, payload)
            results.append(result)
            if result.get("success"):
                success_count += 1
            else:
                failed_count += 1
        state = "done"
        if failed_count and success_count:
            state = "partial"
        elif failed_count:
            state = "failed"
        sync_id = sync_id or self._request_id("SYNC")
        Sync.create(
            {
                "sync_id": sync_id,
                "user_id": user.id,
                "warehouse_id": warehouse.id if warehouse else False,
                "device_id": (payload.get("device_id") or getattr(token, "device_id", "") or "").strip(),
                "request_count": len(requests_payload),
                "success_count": success_count,
                "failed_count": failed_count,
                "results_json": self._dumps_json(results),
                "state": state,
            }
        )
        return {
            "sync_id": sync_id,
            "state": state,
            "request_count": len(requests_payload),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results,
        }

    def _get_sync(self, user, warehouse, sync_id):
        domain = [("sync_id", "=", sync_id)]
        if warehouse:
            domain.append(("warehouse_id", "=", warehouse.id))
        sync = request.env["wms.pda.offline.sync"].with_user(user).sudo().search(domain, limit=1)
        if not sync:
            raise ValidationError("offline sync record does not exist.")
        return self._format_sync(sync)

    def _format_sync(self, sync):
        return {
            "sync_id": sync.sync_id,
            "state": sync.state,
            "request_count": sync.request_count,
            "success_count": sync.success_count,
            "failed_count": sync.failed_count,
            "results": self._loads_json(sync.results_json),
            "create_date": sync.create_date,
        }

    def _process_item(self, index, item, user, warehouse, token, parent_payload):
        try:
            if not isinstance(item, dict):
                raise ValidationError("offline item must be an object.")
            method = (item.get("method") or "POST").upper()
            endpoint = (item.get("endpoint") or item.get("path") or "").strip().rstrip("/")
            item_payload = dict(item.get("payload") or {})
            request_id = (item.get("request_id") or item_payload.get("request_id") or "").strip()
            if not request_id:
                raise ValidationError("request_id is required for offline item.")
            if method != "POST":
                raise ValidationError("offline sync only supports POST actions.")
            item_payload.setdefault("request_id", request_id)
            if parent_payload.get("device_id") and not item_payload.get("device_id"):
                item_payload["device_id"] = parent_payload.get("device_id")
            result = self._run_idempotent(
                item_payload,
                user,
                warehouse,
                token,
                lambda: self._dispatch_item(endpoint, item_payload, user, warehouse, token),
                endpoint=endpoint,
                method=method,
            )
            response_payload = self._response_payload(result)
            return {
                "index": index,
                "request_id": request_id,
                "endpoint": endpoint,
                "method": method,
                "success": self._response_is_success(response_payload),
                "response": response_payload,
            }
        except Exception as exc:
            return {
                "index": index,
                "request_id": item.get("request_id") if isinstance(item, dict) else "",
                "endpoint": item.get("endpoint") if isinstance(item, dict) else "",
                "method": item.get("method") if isinstance(item, dict) else "",
                "success": False,
                "response": {"code": self.ERR_BAD_PARAM, "message": str(exc), "data": {}},
            }

    def _dispatch_item(self, endpoint, payload, user, warehouse, token):
        controllers = self._controllers()
        match = self._match(endpoint, r"/api/pda/wms/v1/receipt/tasks/(\d+)/confirm-line")
        if match:
            return controllers["receipt"]._confirm_line(user, warehouse, int(match.group(1)), payload)
        match = self._match(endpoint, r"/api/pda/wms/v1/receipt/tasks/(\d+)/complete")
        if match:
            return controllers["receipt"]._complete_task(user, warehouse, int(match.group(1)))
        match = self._match(endpoint, r"/api/pda/wms/v1/putaway/tasks/(\d+)/confirm")
        if match:
            return controllers["putaway"]._confirm_putaway(user, warehouse, int(match.group(1)), payload)
        match = self._match(endpoint, r"/api/pda/wms/v1/putaway/tasks/(\d+)/complete")
        if match:
            return controllers["putaway"]._complete_task(user, warehouse, int(match.group(1)))
        match = self._match(endpoint, r"/api/pda/wms/v1/pick/tasks/(\d+)/confirm-line")
        if match:
            return controllers["pick"]._confirm_line(user, warehouse, int(match.group(1)), payload)
        match = self._match(endpoint, r"/api/pda/wms/v1/pick/tasks/(\d+)/complete")
        if match:
            return controllers["pick"]._complete_task(user, warehouse, int(match.group(1)), payload)
        match = self._match(endpoint, r"/api/pda/wms/v1/check/tasks/(\d+)/confirm-line")
        if match:
            return controllers["check"]._confirm_line(user, warehouse, int(match.group(1)), payload)
        match = self._match(endpoint, r"/api/pda/wms/v1/check/tasks/(\d+)/complete")
        if match:
            return controllers["check"]._complete_task(user, warehouse, int(match.group(1)), payload)
        match = self._match(endpoint, r"/api/pda/wms/v1/handover/orders/(\d+)/confirm")
        if match:
            return controllers["handover"]._confirm_order(user, warehouse, int(match.group(1)))
        match = self._match(endpoint, r"/api/pda/wms/v1/handover/orders/(\d+)/complete")
        if match:
            return controllers["handover"]._complete_order(user, warehouse, int(match.group(1)))
        match = self._match(endpoint, r"/api/pda/wms/v1/handover/orders/(\d+)/prepare-route-batch")
        if match:
            return controllers["handover"]._prepare_route_batch(user, warehouse, int(match.group(1)))
        if endpoint == "/api/pda/wms/v1/return/create":
            return controllers["warehouse_return"]._create_operation(user, warehouse, payload)
        match = self._match(endpoint, r"/api/pda/wms/v1/return/(\d+)/add-line")
        if match:
            return controllers["warehouse_return"]._add_line(user, warehouse, int(match.group(1)), payload)
        match = self._match(endpoint, r"/api/pda/wms/v1/return/(\d+)/confirm")
        if match:
            return controllers["warehouse_return"]._confirm_operation(user, warehouse, int(match.group(1)))
        match = self._match(endpoint, r"/api/pda/wms/v1/sale-return/tasks/(\d+)/confirm-line")
        if match:
            return controllers["sale_return"]._confirm_line(user, warehouse, int(match.group(1)), payload)
        match = self._match(endpoint, r"/api/pda/wms/v1/sale-return/tasks/(\d+)/complete")
        if match:
            return controllers["sale_return"]._complete_task(user, warehouse, int(match.group(1)), payload)
        if endpoint == "/api/pda/wms/v1/photos/upload":
            return controllers["photos"]._upload(user, warehouse, token, payload)
        if endpoint == "/api/pda/wms/v1/photos/bind":
            return controllers["photos"]._bind(user, warehouse, token, payload)
        raise ValidationError("unsupported offline endpoint.")

    def _controllers(self):
        from .check import WmsPdaCheckController
        from .handover import WmsPdaHandoverController
        from .photos import WmsPdaPhotosController
        from .pick import WmsPdaPickController
        from .putaway import WmsPdaPutawayController
        from .receipt import WmsPdaReceiptController
        from .sale_return import WmsPdaSaleReturnController
        from .warehouse_return import WmsPdaWarehouseReturnController

        return {
            "receipt": WmsPdaReceiptController(),
            "putaway": WmsPdaPutawayController(),
            "pick": WmsPdaPickController(),
            "check": WmsPdaCheckController(),
            "handover": WmsPdaHandoverController(),
            "warehouse_return": WmsPdaWarehouseReturnController(),
            "sale_return": WmsPdaSaleReturnController(),
            "photos": WmsPdaPhotosController(),
        }

    def _match(self, endpoint, pattern):
        return re.fullmatch(pattern, endpoint)
