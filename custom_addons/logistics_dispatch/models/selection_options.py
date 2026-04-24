from odoo.addons.logistics_base.models.selection_options import (
    DRIVER_DISPATCH_STATUS_SELECTION,
    SHIFT_TYPE_SELECTION,
    VEHICLE_DISPATCH_STATUS_SELECTION,
)

PAYMENT_STATUS_SELECTION = [
    ("unpaid", "未付款"),
    ("partial_paid", "部分付款"),
    ("paid", "已付款"),
]

AUDIT_STATUS_SELECTION = [
    ("unaudited", "未审核"),
    ("audited", "已审核"),
    ("rejected", "审核驳回"),
]

SETTLEMENT_STATUS_SELECTION = [
    ("unsettled", "未结算"),
    ("partial_settled", "部分结算"),
    ("settled", "已结算"),
]

DOC_STATUS_SELECTION = [
    ("draft", "草稿"),
    ("confirmed", "已确认"),
    ("cancelled", "已取消"),
]

LOGISTICS_STATUS_SELECTION = [
    ("pending_outbound", "待出库"),
    ("outbounded", "已出库"),
    ("delivering", "配送中"),
    ("signed", "已签收"),
    ("abnormal", "异常"),
]

IMPORT_TASK_STATUS_SELECTION = [
    ("pending", "待执行"),
    ("running", "执行中"),
    ("success", "全部成功"),
    ("partial_failed", "部分失败"),
    ("failed", "全部失败"),
    ("cancelled", "已取消"),
]

IMPORT_TASK_LINE_STATUS_SELECTION = [
    ("pending", "待处理"),
    ("success", "成功"),
    ("failed", "失败"),
    ("skipped", "跳过"),
]

IMPORT_OBJECT_TYPE_SELECTION = [
    ("customer_profile", "客户经营画像"),
    ("store_profile", "门店配送画像"),
    ("driver_profile", "司机主数据"),
    ("vehicle_profile", "车辆主数据"),
    ("dispatch_main", "波次/批次/运单主链"),
    ("image_package", "图片包导入"),
]
