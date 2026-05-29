# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class LogisticsWebRootRedirect(http.Controller):
    @http.route("/", type="http", auth="none", website=False, sitemap=False)
    def logistics_web_root(self, **kwargs):
        query = ""
        if request.db:
            query = "?db=%s" % request.db
        return request.redirect("/web/login%s" % query)
