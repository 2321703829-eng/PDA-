from odoo import http
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaWorkbenchController(WmsPdaBaseController):
    @http.route("/api/pda/wms/v1/workbench/summary", type="http", auth="public", methods=["GET"], csrf=False)
    def workbench_summary(self, **kwargs):
        return self._handle_request(lambda user, wh, token: self._summary(user, wh))

    def _summary(self, user, warehouse):
        return {
            "warehouse": {
                "id": warehouse.id if warehouse else False,
                "name": warehouse.display_name if warehouse else "",
            },
            "todos": [
                self._todo("receipt", "待收货", "inbound-flow", "inbound", self._count("wms.receipt.task", warehouse, ["waiting_receipt", "receiving"])),
                self._todo("putaway", "待上架", "inbound-flow", "putaway", self._count("wms.putaway.task", warehouse, ["waiting_putaway", "putaway_ing"])),
                self._todo("pick", "待拣货", "outbound-flow", "pick", self._count("wms.pick.task", warehouse, ["waiting_pick", "picking"])),
                self._todo("check", "待复核", "outbound-flow", "outbound", self._count("wms.check.task", warehouse, ["waiting_check", "checking"])),
                self._todo("exception", "异常待处理", "exceptions", "", self._exception_count(warehouse)),
            ],
        }

    def _todo(self, key, label, route, mode, count):
        return {
            "key": key,
            "label": label,
            "route": route,
            "mode": mode,
            "count": count,
        }

    def _count(self, model_name, warehouse, states):
        if model_name not in request.env.registry:
            return 0
        domain = [("state", "in", states)]
        if warehouse:
            domain.append(("warehouse_id", "=", warehouse.id))
        return request.env[model_name].sudo().search_count(domain)

    def _exception_count(self, warehouse):
        specs = (
            ("wms.receipt.task", ["receipt_exception"]),
            ("wms.putaway.task", ["putaway_exception"]),
            ("wms.pick.task", ["pick_exception"]),
            ("wms.check.task", ["check_exception"]),
        )
        total = 0
        for model_name, states in specs:
            total += self._count(model_name, warehouse, states)
        return total
