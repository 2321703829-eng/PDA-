{
    "name": "Logistics Trace Evidence",
    "version": "19.0.1.0.0",
    "summary": "Evidence model for logistics trace events",
    "author": "OpenAI",
    "license": "LGPL-3",
    "depends": [
        "logistics_trace_core",
    ],
    "data": [
        "security/logistics_trace_evidence_security.xml",
        "security/ir.model.access.csv",
        "views/logistics_trace_evidence_views.xml",
    ],
    "installable": True,
    "application": False,
    "post_init_hook": "post_init_hook",
}
