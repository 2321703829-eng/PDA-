from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaPhotosController(WmsPdaBaseController):
    ALLOWED_TASK_MODELS = {
        "wms.receipt.task",
        "wms.putaway.task",
        "wms.outbound.task",
        "wms.pick.task",
        "wms.check.task",
        "wms.handover.order",
        "wms.inventory.operation",
    }

    @http.route("/api/pda/wms/v1/photos/upload", type="http", auth="public", methods=["POST"], csrf=False)
    def upload_photos(self, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._upload(user, wh, token, payload))

    @http.route("/api/pda/wms/v1/photos/bind", type="http", auth="public", methods=["POST"], csrf=False)
    def bind_photos(self, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._bind(user, wh, token, payload))

    @http.route("/api/pda/wms/v1/photos", type="http", auth="public", methods=["GET"], csrf=False)
    def list_photos(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._list(user, wh, payload))

    def _upload(self, user, warehouse, token, payload):
        urls = self._photo_urls(payload)
        if payload.get("task_model") and payload.get("task_id"):
            return self._bind(user, warehouse, token, payload)
        return {
            "uploaded": True,
            "bound": False,
            "photo_urls": urls,
            "message": "photo_url accepted; call /photos/bind with task_model and task_id to bind it.",
        }

    def _bind(self, user, warehouse, token, payload):
        urls = self._photo_urls(payload)
        task = self._get_task(user, warehouse, payload)
        Photo = request.env["wms.task.photo"].sudo()
        device_id = (payload.get("device_id") or getattr(token, "device_id", "") or "").strip()
        photos = Photo.browse()
        for url in urls:
            photos |= Photo.create(
                {
                    "task_model": task._name,
                    "task_id": task.id,
                    "photo_url": url,
                    "operator_id": user.id,
                    "warehouse_id": warehouse.id if warehouse else self._task_warehouse_id(task),
                    "device_id": device_id,
                    "gps": (payload.get("gps") or "").strip(),
                    "note": (payload.get("note") or "").strip(),
                }
            )
        return {
            "bound": True,
            "task_model": task._name,
            "task_id": task.id,
            "photo_count": len(photos),
            "photos": [self._format_photo(photo) for photo in photos],
        }

    def _list(self, user, warehouse, payload):
        task = self._get_task(user, warehouse, payload)
        photos = request.env["wms.task.photo"].sudo().search(
            [("task_model", "=", task._name), ("task_id", "=", task.id)],
            order="id desc",
        )
        return {
            "task_model": task._name,
            "task_id": task.id,
            "photo_count": len(photos),
            "photos": [self._format_photo(photo) for photo in photos],
        }

    def _get_task(self, user, warehouse, payload):
        model_name = (payload.get("task_model") or "").strip()
        task_id = int(payload.get("task_id") or 0)
        if model_name not in self.ALLOWED_TASK_MODELS:
            raise ValidationError("unsupported task_model.")
        if not task_id:
            raise ValidationError("task_id is required.")
        if model_name not in request.env:
            raise ValidationError("task model is not installed.")
        task = request.env[model_name].with_user(user).sudo().browse(task_id).exists()
        if not task:
            raise ValidationError("task does not exist.")
        task_warehouse_id = self._task_warehouse_id(task)
        if warehouse and task_warehouse_id and task_warehouse_id != warehouse.id:
            raise ValidationError("task does not belong to current warehouse.")
        return task

    def _task_warehouse_id(self, task):
        if "warehouse_id" in task._fields and task.warehouse_id:
            return task.warehouse_id.id
        if "outbound_task_id" in task._fields and task.outbound_task_id and task.outbound_task_id.warehouse_id:
            return task.outbound_task_id.warehouse_id.id
        if "stock_picking_id" in task._fields and task.stock_picking_id and task.stock_picking_id.picking_type_id.warehouse_id:
            return task.stock_picking_id.picking_type_id.warehouse_id.id
        return False

    def _photo_urls(self, payload):
        urls = payload.get("photo_urls") or payload.get("photo_url")
        if isinstance(urls, str):
            urls = [urls]
        if not isinstance(urls, list):
            raise ValidationError("photo_url or photo_urls is required.")
        result = [(url or "").strip() for url in urls if (url or "").strip()]
        if not result:
            raise ValidationError("photo_url or photo_urls is required.")
        return result

    def _format_photo(self, photo):
        return {
            "id": photo.id,
            "task_model": photo.task_model,
            "task_id": photo.task_id,
            "photo_url": photo.photo_url,
            "operator_id": photo.operator_id.id if photo.operator_id else False,
            "operator_name": photo.operator_id.display_name if photo.operator_id else "",
            "warehouse_id": photo.warehouse_id.id if photo.warehouse_id else False,
            "warehouse_name": photo.warehouse_id.display_name if photo.warehouse_id else "",
            "device_id": photo.device_id or "",
            "gps": photo.gps or "",
            "note": photo.note or "",
            "create_date": photo.create_date,
        }

