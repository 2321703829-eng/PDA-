from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaAuthController(WmsPdaBaseController):
    @http.route("/api/pda/wms/v1/auth/login", type="http", auth="public", methods=["POST"], csrf=False)
    def pda_login(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._login(payload), require_auth=False)

    @http.route("/api/pda/wms/v1/auth/switch-warehouse", type="http", auth="public", methods=["POST"], csrf=False)
    def switch_warehouse(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._switch_warehouse(user, token, payload))

    def _login(self, payload):
        login = (payload.get("login") or "").strip()
        password = payload.get("password") or ""
        device_id = (payload.get("device_id") or "").strip()
        if not login or not password:
            raise ValidationError("请输入账号和密码。")
        uid = self._authenticate_password(login, password)
        if not uid:
            raise AccessError("账号或密码错误。")
        user = request.env["res.users"].sudo().browse(uid)
        if not self._has_group(uid, "wms_pda_api.group_pda_user"):
            raise AccessError("当前用户没有 PDA 仓库作业权限。")
        warehouses = self._available_warehouses(uid)
        default_warehouse = warehouses[:1]
        token = request.env["wms.api.token"].sudo().generate_token(
            uid,
            device_id=device_id or False,
            warehouse_id=default_warehouse.id if default_warehouse else False,
        )
        return {
            "token": token.token,
            "expires_in": 86400,
            "user": {
                "id": user.id,
                "name": user.display_name,
                "role": self._role_for_user(user),
            },
            "warehouses": [
                {"id": warehouse.id, "name": warehouse.display_name}
                for warehouse in warehouses
            ],
            "current_warehouse_id": token.warehouse_id.id if token.warehouse_id else False,
        }

    def _authenticate_password(self, login, password):
        try:
            uid = request.session.authenticate(request.db, login, password)
        except TypeError:
            credential = {"login": login, "password": password, "type": "password"}
            uid = request.session.authenticate(request.db, credential)
        return uid or request.session.uid

    def _available_warehouses(self, user_id):
        Warehouse = request.env["stock.warehouse"].with_user(user_id).sudo()
        return Warehouse.search([], order="id asc")

    def _role_for_user(self, user):
        if self._has_group(user.id, "wms_pda_api.group_pda_admin"):
            return "warehouse_admin"
        if self._has_group(user.id, "wms_pda_api.group_pda_leader"):
            return "warehouse_leader"
        return "warehouse_worker"

    def _has_group(self, user_id, xmlid):
        return request.env["res.users"].with_user(user_id).has_group(xmlid)

    def _switch_warehouse(self, user, token, payload):
        warehouse_id = int(payload.get("warehouse_id") or 0)
        if not warehouse_id:
            raise ValidationError("请选择仓库。")
        warehouse = request.env["stock.warehouse"].sudo().browse(warehouse_id).exists()
        if not warehouse:
            raise ValidationError("仓库不存在。")
        if warehouse not in self._available_warehouses(user.id):
            raise AccessError("当前用户没有该仓库权限。")
        token.write({"warehouse_id": warehouse.id})
        location_count = request.env["stock.location"].sudo().search_count(
            [
                "|",
                ("id", "child_of", warehouse.view_location_id.id),
                ("id", "=", warehouse.lot_stock_id.id),
            ]
        )
        return {
            "warehouse_id": warehouse.id,
            "warehouse_name": warehouse.display_name,
            "location_count": location_count,
        }
