# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


SOLUTION_PAGES = {
    "warehouse": {
        "title": "数字仓储",
        "eyebrow": "WMS Warehouse Operations",
        "summary": "把收货、上架、出库、拣货、复核、交接串成一条清晰的仓内作业链路。",
        "points": [
            "以任务驱动作业人员执行，减少口头交接和人工漏记。",
            "库存台账、作业节点、异常记录统一留痕，方便复盘。",
            "支持与运输调度联动，让仓库出库节奏直接服务配送计划。",
        ],
    },
    "dispatch": {
        "title": "运输调度",
        "eyebrow": "TMS Dispatch Control",
        "summary": "围绕批次、路线、车辆、司机任务和签收节点，管理从派车到到店的全过程。",
        "points": [
            "按线路和停靠点组织配送任务，减少重复排线和漏派。",
            "司机任务状态回流后台，调度人员能快速看到在途、到店、签收和异常。",
            "为城市配送场景保留可扩展的费用、时效、车辆和司机画像数据。",
        ],
    },
    "trace": {
        "title": "留痕可视",
        "eyebrow": "Trace Evidence Center",
        "summary": "以运单为主对象，沉淀到店、签收、异常、图片证据和处理记录。",
        "points": [
            "仓库、司机、门店侧关键节点统一进入留痕时间线。",
            "异常与证据关联，减少追责时反复翻聊天记录和图片。",
            "让管理层从单票详情到整体履约质量都能快速定位问题。",
        ],
    },
}


class KebiHomepageController(http.Controller):

    @http.route(["/", "/zh_CN", "/zh_CN/"], type="http", auth="public", website=True, sitemap=True)
    def homepage(self, **kw):
        return request.render("kebi_website_custom.homepage_template", {})

    @http.route(
        ["/solutions/<string:slug>", "/zh_CN/solutions/<string:slug>"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def solution_detail(self, slug, **kw):
        page = SOLUTION_PAGES.get(slug)
        if not page:
            return request.not_found()
        return request.render("kebi_website_custom.solution_detail_template", {"page": page})

    @http.route(
        ["/register", "/zh_CN/register"],
        type="http",
        auth="public",
        website=True,
        methods=["GET", "POST"],
        sitemap=True,
    )
    def mock_register(self, **kw):
        submitted = request.httprequest.method == "POST"
        if submitted:
            request.env["kebi.registration.request"].sudo().create({
                "name": (kw.get("name") or "").strip() or "未填写",
                "company": (kw.get("company") or "").strip(),
                "contact": (kw.get("login") or "").strip() or "未填写",
                "message": (kw.get("message") or "").strip(),
                "request_ip": request.httprequest.headers.get(
                    "X-Forwarded-For", request.httprequest.remote_addr or ""
                ),
                "user_agent": request.httprequest.headers.get("User-Agent", "")[:255],
            })
        return request.render(
            "kebi_website_custom.mock_register_template",
            {
                "submitted": submitted,
                "name": kw.get("name", ""),
                "login": kw.get("login", ""),
                "company": kw.get("company", ""),
            },
        )

    @http.route(
        ["/register/requests", "/zh_CN/register/requests"],
        type="http",
        auth="user",
        website=True,
        sitemap=False,
    )
    def registration_requests(self, **kw):
        if not request.env.user.has_group("base.group_system"):
            return request.not_found()
        records = request.env["kebi.registration.request"].sudo().search([], order="create_date desc", limit=80)
        return request.render(
            "kebi_website_custom.registration_request_list_template",
            {"records": records},
        )
