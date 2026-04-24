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
    ("route_planning", "排线用数据导入"),
    ("image_package", "图片包导入"),
]

EXPORT_OBJECT_TYPE_SELECTION = [
    ("dispatch_main", "标准主链导出"),
    ("customer_profile", "统一客户画像导出"),
    ("product_profile", "货物画像导出"),
]

EXPORT_ENTRY_TYPE_SELECTION = [
    ("from_batch", "从批次导出"),
    ("from_waybill", "从运单导出"),
    ("from_customer", "从客户导出"),
    ("from_product", "从商品导出"),
]

EXPORT_MODE_SELECTION = [
    ("standard_xlsx", "标准四Sheet导出"),
]

EXPORT_PACKAGE_STRUCTURE_SELECTION = [
    ("dispatch_main_four_sheet", "标准主链四Sheet"),
    ("customer_profile_bundle_v1", "客户画像单Sheet"),
    ("customer_profile_bundle_v2", "客户画像加客户商品关系"),
    ("product_profile_bundle_v1", "货物画像与商品规格"),
    ("product_profile_bundle_v2", "货物画像、商品规格加客户商品关系"),
]

EXPORT_TARGET_OBJECT_TYPE_SELECTION = [
    ("batch", "批次"),
    ("waybill", "运单"),
    ("customer", "客户"),
    ("partner", "客户画像"),
    ("product", "货物画像"),
]

EXPORT_TASK_STATUS_SELECTION = [
    ("pending", "待执行"),
    ("running", "执行中"),
    ("success", "全部成功"),
    ("partial_failed", "部分失败"),
    ("failed", "全部失败"),
    ("expired", "已过期"),
    ("cancelled", "已取消"),
]

EXPORT_TASK_LINE_STATUS_SELECTION = [
    ("pending", "待处理"),
    ("success", "成功"),
    ("failed", "失败"),
    ("skipped", "跳过"),
]

EXPORT_ERROR_STAGE_SELECTION = [
    ("scope_validate", "范围校验"),
    ("target_resolve", "对象命中"),
    ("data_collect", "数据收集"),
    ("workbook_build", "工作簿构建"),
    ("file_store", "文件落盘"),
    ("download_prepare", "下载准备"),
]
