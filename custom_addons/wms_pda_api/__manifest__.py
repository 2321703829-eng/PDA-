{
    "name": "WMS PDA API",
    "version": "19.0.1.0.0",
    "summary": "PDA server foundation for warehouse operations",
    "author": "OpenAI",
    "license": "LGPL-3",
    "depends": [
        "wms_task_core",
    ],
    "data": [
        "security/wms_pda_security.xml",
        "security/ir.model.access.csv",
        "views/wms_pda_views.xml",
    ],
    "installable": True,
    "application": False,
}
