import hashlib

from odoo import http
from odoo.http import request
from odoo.tools import file_open


class WmsPdaH5Controller(http.Controller):
    @http.route(["/pda", "/pda/"], type="http", auth="public", website=False, csrf=False)
    def pda_h5(self, **kwargs):
        with file_open("wms_pda_api/static/pda/index.html") as handle:
            html = handle.read()
        css_version = self._asset_version("wms_pda_api/static/pda/assets/pda.css")
        js_version = self._asset_version("wms_pda_api/static/pda/assets/pda.js")
        html = html.replace(
            'href="./assets/pda.css"',
            f'href="/wms_pda_api/static/pda/assets/pda.css?v={css_version}"',
        )
        html = html.replace(
            'src="./assets/pda.js"',
            f'src="/wms_pda_api/static/pda/assets/pda.js?v={js_version}"',
        )
        return request.make_response(
            html,
            headers=[
                ("Content-Type", "text/html; charset=utf-8"),
                ("Cache-Control", "no-store, max-age=0"),
                ("Pragma", "no-cache"),
            ],
        )

    def _asset_version(self, addon_path):
        try:
            with file_open(addon_path, "rb") as handle:
                return hashlib.sha1(handle.read()).hexdigest()[:12]
        except FileNotFoundError:
            return "dev"
