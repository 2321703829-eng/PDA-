from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaBarcodeController(WmsPdaBaseController):
    @http.route("/api/pda/wms/v1/barcode/parse", type="http", auth="public", methods=["POST"], csrf=False)
    def parse_barcode(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._parse_barcode(wh, payload))

    def _parse_barcode(self, warehouse, payload):
        barcode = (payload.get("barcode") or "").strip()
        if not barcode:
            raise ValidationError("请扫描或输入条码。")
        result = request.env["wms.pda.barcode.parser"].sudo().parse_barcode(barcode, warehouse=warehouse)
        if result.get("type") == "unknown":
            return self._error(
                self.ERR_BARCODE_UNKNOWN,
                "条码无法识别。",
                status=400,
                data={"barcode": barcode},
                tts="未识别",
            )
        return result
