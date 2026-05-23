{
    "name": "BI Ops Dashboard",
    "version": "19.0.1.0.0",
    "summary": "BI snapshot skeleton for order, warehouse, dispatch and profit dashboards",
    "author": "OpenAI",
    "license": "LGPL-3",
    "depends": [
        "mail",
        "erp_base",
        "core_operation_audit_log",
        "logistics_base",
        "wms_task_core",
        "tms_dispatch_core",
    ],
    "data": [
        "security/bi_ops_dashboard_security.xml",
        "security/ir.model.access.csv",
        "views/bi_snapshot_views.xml",
    ],
    "installable": True,
    "application": False,
}
