{
    "name": "Logistics Trace Core",
    "summary": "Batch-level and waybill-level logistics trace events",
    "version": "1.0.0",
    "category": "Inventory/Inventory",
    "author": "Tian Shu",
    "license": "LGPL-3",
    "depends": ["stock"],
    "data": [
        "data/ir_sequence_data.xml",
        "security/ir.model.access.csv",
        "views/logistics_trace_event_views.xml",
        "views/logistics_waybill_stop_views.xml",
        "views/logistics_trace_menu.xml",
    ],
    "installable": True,
    "application": True,
}
