TMS_ROUTE_STATUS_SELECTION = [
    ("waiting_route", "待排线"),
    ("route_planned", "已排线"),
    ("route_confirmed", "已确认"),
]

TMS_DISPATCH_STATUS_SELECTION = [
    ("waiting_dispatch", "待派车"),
    ("dispatched", "已派车"),
    ("departed", "已发车"),
    ("in_transit", "在途"),
    ("arrived_store", "已到店"),
    ("signed_full", "全签"),
    ("signed_partial", "部分签收"),
    ("delivery_exception", "配送异常"),
]

TMS_DRIVER_NODE_STATUS_SELECTION = [
    ("driver_arrived_warehouse", "司机到仓"),
    ("departed", "已发车"),
    ("in_transit", "在途"),
    ("arrived_store", "已到店"),
    ("delivering", "配送中"),
]

TMS_EXCEPTION_TYPE_SELECTION = [
    ("delay", "延误"),
    ("damage", "破损"),
    ("shortage", "短少"),
    ("reject", "拒收"),
    ("no_receiver", "门店无人"),
]

TMS_FREIGHT_FEE_TYPE_SELECTION = [
    ("trip_fee", "车次费"),
    ("mileage_fee", "里程费"),
    ("stop_fee", "点位费"),
    ("addon_fee", "附加费"),
    ("deduction_fee", "扣款"),
]
