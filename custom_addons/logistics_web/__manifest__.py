{
    "name": "Logistics Web",
    "version": "19.0.1.0.0",
    "summary": "Frontend enhancement layer for the Odoo logistics backend",
    "license": "LGPL-3",
    "depends": [
        "web",
        "logistics_dispatch",
        "logistics_trace_core",
        "logistics_trace_evidence",
        "logistics_trace_exception",
    ],
    "data": [
        "views/logistics_web_actions.xml",
        "views/logistics_web_menus.xml",
        "views/logistics_web_templates.xml",
        "views/logistics_web_waybill_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "logistics_web/static/src/js/actions/*.js",
            "logistics_web/static/src/js/components/*.js",
            "logistics_web/static/src/js/services/*.js",
            "logistics_web/static/src/js/views/*.js",
            "logistics_web/static/src/js/widgets/*.js",
            "logistics_web/static/src/xml/*.xml",
            "logistics_web/static/src/scss/*.scss",
        ],
    },
    "installable": True,
    "application": False,
}
