{
    "name": "Logistics Dispatch",
    "version": "18.0.1.0.0",
    "summary": "Dispatch execution mainline for waves, batches, and waybills",
    "license": "LGPL-3",
    "depends": [
        "logistics_base",
        "mail",
        "fleet",
        "sale",
        "stock_picking_batch",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence_data.xml",
        "views/logistics_dispatch_wave_views.xml",
        "views/logistics_dispatch_batch_views.xml",
        "views/logistics_dispatch_waybill_views.xml",
        "views/logistics_dispatch_menus.xml",
    ],
    "installable": True,
    "application": True,
}

