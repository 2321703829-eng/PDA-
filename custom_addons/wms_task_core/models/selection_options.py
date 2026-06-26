WMS_LOCATION_USAGE_TYPE_EXT_SELECTION = [
    ("pick_face", "拣货面"),
    ("bulk", "散货区"),
    ("staging", "暂存区"),
    ("handover", "交接区"),
    ("count_zone", "盘点区"),
]

WMS_RECEIPT_TASK_STATUS_SELECTION = [
    ("waiting_receipt", "待收货"),
    ("receiving", "收货中"),
    ("received", "已收货"),
    ("closed", "已关单"),
    ("receipt_exception", "收货异常"),
]

WMS_PUTAWAY_TASK_STATUS_SELECTION = [
    ("waiting_putaway", "待上架"),
    ("putaway_ing", "上架中"),
    ("putaway_done", "已上架"),
    ("putaway_exception", "上架异常"),
]

WMS_OUTBOUND_TASK_STATUS_SELECTION = [
    ("waiting_outbound", "待出库"),
    ("task_created", "已创建"),
    ("task_processing", "处理中"),
    ("task_done", "已完成"),
    ("task_exception", "出库异常"),
]

WMS_PICK_TASK_STATUS_SELECTION = [
    ("waiting_pick", "待拣货"),
    ("picking", "拣货中"),
    ("picked", "已拣货"),
    ("pick_exception", "拣货异常"),
]

WMS_CHECK_TASK_STATUS_SELECTION = [
    ("waiting_check", "待复核"),
    ("checking", "复核中"),
    ("checked", "已复核"),
    ("check_exception", "复核异常"),
]

WMS_HANDOVER_STATUS_SELECTION = [
    ("waiting_handover", "待交接"),
    ("handover_ing", "交接中"),
    ("handover_done", "已交接"),
    ("handover_exception", "交接异常"),
]

ERP_SOURCE_TYPE_SELECTION = [
    ("sale", "销售"),
    ("purchase", "采购"),
    ("sale_return", "销售退货"),
    ("purchase_return", "采购退货"),
    ("internal", "内部调拨"),
]
