{
    "name": "Logistics Trace Core",
    "version": "19.0.1.0.0",
    "summary": "Core trace event model for batches and waybills",
    "license": "LGPL-3",
    "depends": [
        "mail",
        "logistics_dispatch",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/logistics_trace_event_views.xml",
    ],
    "installable": True,
    "application": False,
}
