{
    "name": "Logistics Base",
    "version": "18.0.1.0.0",
    "summary": "Logistics master data extensions",
    "license": "LGPL-3",
    "depends": [
        "contacts",
        "hr",
        "stock",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/hr_employee_views.xml",
        "views/stock_warehouse_views.xml",
        "views/logistics_base_menus.xml",
    ],
    "installable": True,
    "application": False,
}
