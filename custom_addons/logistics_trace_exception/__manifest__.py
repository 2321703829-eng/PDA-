{
    "name": "Logistics Trace Exception",
    "version": "19.0.1.0.0",
    "summary": "物流留痕异常管理层",
    "author": "OpenAI",
    "license": "LGPL-3",
    "depends": [
        "mail",
        "hr",
        "logistics_trace_core",
        "logistics_trace_evidence",
    ],
    "data": [
        "security/logistics_trace_exception_security.xml",
        "security/ir.model.access.csv",
        "views/logistics_trace_exception_views.xml",
    ],
    "installable": True,
    "application": False,
}
