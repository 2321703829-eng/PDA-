# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class KebiProfileController(http.Controller):

    @http.route("/my/profile", type="http", auth="user", website=True)
    def profile(self, **kw):
        partner = request.env.user.partner_id
        stores = request.env["res.partner"].sudo().search(
            [("is_b2b_store", "=", True)], limit=20)
        if not stores:
            stores = request.env["res.partner"].sudo().search(
                [("is_company", "=", True)], limit=10)

        msg = kw.get("msg", "")
        values = {
            "partner": partner,
            "stores": stores,
            "msg": msg,
            "phone": partner.phone or partner.mobile or "",
            "email": partner.email or "",
            "default_store_id": partner.b2b_default_store_id,
            "delivery_note": partner.delivery_note or "",
        }
        return request.render("kebi_website_custom.profile_template", values)

    @http.route("/my/profile/save", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def profile_save(self, **kw):
        partner = request.env.user.partner_id
        vals = {}
        if kw.get("phone"):
            vals["phone"] = kw["phone"]
        if kw.get("email"):
            vals["email"] = kw["email"]
        if kw.get("default_store_id"):
            vals["b2b_default_store_id"] = int(kw["default_store_id"])
        if "delivery_note" in kw:
            vals["delivery_note"] = kw.get("delivery_note", "")
        if vals:
            partner.sudo().write(vals)
        return request.redirect("/my/profile?msg=saved")
