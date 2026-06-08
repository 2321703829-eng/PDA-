from odoo import http

from .base import WmsPdaBaseController


class WmsPdaConfigController(WmsPdaBaseController):
    @http.route("/api/pda/wms/v1/config/options", type="http", auth="public", methods=["GET"], csrf=False)
    def get_options(self, **kwargs):
        return self._handle_request(lambda user, wh, token: self._get_options())

    def _get_options(self):
        return {
            "return_reasons": [
                {"value": "damaged", "label": "破损"},
                {"value": "expired", "label": "过期"},
                {"value": "oversupply", "label": "补货过多"},
                {"value": "slow_moving", "label": "不好卖"},
                {"value": "other", "label": "其他"},
            ],
            "quality_states": [
                {"value": "good", "label": "完好"},
                {"value": "damaged", "label": "损坏"},
                {"value": "expired", "label": "过期"},
            ],
            "operation_types": [
                {"value": "warehouse_return", "label": "退供应商"},
                {"value": "internal_return", "label": "退仓"},
            ],
        }
