CUSTOMER_STATUS_SELECTION = [
    ("normal", "正常"),
    ("disabled", "停用"),
    ("frozen", "冻结"),
]

LOGISTICS_ROLE_SELECTION = [
    ("dispatcher", "调度"),
    ("customer_service", "客服"),
    ("warehouse_keeper", "仓管"),
    ("driver", "司机"),
    ("operator", "操作员"),
    ("manager", "管理人员"),
]

DRIVER_DISPATCH_STATUS_SELECTION = [
    ("idle", "空闲可调度"),
    ("assigned", "已被当前批次占用"),
    ("off_duty", "不在班/不可参与当前排线"),
    ("disabled", "停用"),
]

VEHICLE_DISPATCH_STATUS_SELECTION = [
    ("idle", "空闲可调度"),
    ("assigned", "已被当前批次占用"),
    ("repair", "维修中/不可调度"),
    ("disabled", "停用"),
]

SHIFT_TYPE_SELECTION = [
    ("day", "day"),
    ("night", "night"),
]
