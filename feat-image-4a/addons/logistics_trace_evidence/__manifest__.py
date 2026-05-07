{
    "name": "Logistics Trace Evidence",
    "summary": "Evidence and image references for logistics trace events",
    "version": "1.0.0",
    "category": "Inventory/Inventory",
    "author": "Tian Shu",
    "license": "LGPL-3",
    "depends": ["logistics_trace_core", "stock"],
    "data": [
        "data/ir_sequence_data.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/logistics_trace_evidence_views.xml",
        "wizards/logistics_trace_evidence_upload_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
}
