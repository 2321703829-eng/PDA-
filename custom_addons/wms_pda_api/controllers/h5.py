from odoo import http
from odoo.http import request
from odoo.tools import file_open


class WmsPdaH5Controller(http.Controller):
    @http.route(["/pda", "/pda/"], type="http", auth="public", website=False, csrf=False)
    def pda_h5(self, **kwargs):
        with file_open("wms_pda_api/static/pda/index.html") as handle:
            html = handle.read()
        html = html.replace('href="./assets/pda.css"', 'href="/wms_pda_api/static/pda/assets/pda.css"')
        html = html.replace('src="./assets/pda.js"', 'src="/wms_pda_api/static/pda/assets/pda.js"')
        return request.make_response(html, headers=[("Content-Type", "text/html; charset=utf-8")])
