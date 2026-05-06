from odoo.addons.logistics_base.models.selection_options import (
    DRIVER_DISPATCH_STATUS_SELECTION,
    SHIFT_TYPE_SELECTION,
    VEHICLE_DISPATCH_STATUS_SELECTION,
)

PAYMENT_STATUS_SELECTION = [
    ("unpaid", "Unpaid"),
    ("partial_paid", "Partial Paid"),
    ("paid", "Paid"),
]

AUDIT_STATUS_SELECTION = [
    ("unaudited", "Unaudited"),
    ("audited", "Audited"),
    ("rejected", "Rejected"),
]

SETTLEMENT_STATUS_SELECTION = [
    ("unsettled", "Unsettled"),
    ("partial_settled", "Partial Settled"),
    ("settled", "Settled"),
]

DOC_STATUS_SELECTION = [
    ("draft", "Draft"),
    ("confirmed", "Confirmed"),
    ("cancelled", "Cancelled"),
]

LOGISTICS_STATUS_SELECTION = [
    ("pending_outbound", "Pending Outbound"),
    ("outbounded", "Outbounded"),
    ("delivering", "Delivering"),
    ("signed", "Signed"),
    ("abnormal", "Abnormal"),
]

IMPORT_TASK_STATUS_SELECTION = [
    ("pending", "Pending"),
    ("running", "Running"),
    ("success", "Success"),
    ("partial_failed", "Partial Failed"),
    ("failed", "Failed"),
    ("cancelled", "Cancelled"),
]

IMPORT_TASK_LINE_STATUS_SELECTION = [
    ("pending", "Pending"),
    ("success", "Success"),
    ("failed", "Failed"),
    ("skipped", "Skipped"),
]

IMPORT_OBJECT_TYPE_SELECTION = [
    ("customer_profile", "Customer Profile"),
    ("store_profile", "Store Profile"),
    ("driver_profile", "Driver Profile"),
    ("vehicle_profile", "Vehicle Profile"),
    ("dispatch_main", "Dispatch Main"),
    ("route_planning", "Route Planning"),
    ("phase5_workbook", "Phase5 Workbook"),
    ("image_package", "Image Package"),
]

EXPORT_OBJECT_TYPE_SELECTION = [
    ("dispatch_main", "Dispatch Main Export"),
    ("customer_profile", "Customer Profile Export"),
    ("product_profile", "Product Profile Export"),
    ("evidence_image_bundle", "Evidence Image Bundle Export"),
]

EXPORT_ENTRY_TYPE_SELECTION = [
    ("from_batch", "From Batch"),
    ("from_waybill", "From Waybill"),
    ("from_evidence", "From Evidence"),
    ("from_customer", "From Customer"),
    ("from_product", "From Product"),
]

EXPORT_MODE_SELECTION = [
    ("standard_xlsx", "Standard XLSX"),
    ("zip_package", "ZIP Package"),
]

EXPORT_PACKAGE_STRUCTURE_SELECTION = [
    ("dispatch_main_four_sheet", "Dispatch Main Four Sheet"),
    ("customer_profile_bundle_v1", "Customer Profile Bundle V1"),
    ("customer_profile_bundle_v2", "Customer Profile Bundle V2"),
    ("product_profile_bundle_v1", "Product Profile Bundle V1"),
    ("product_profile_bundle_v2", "Product Profile Bundle V2"),
    ("evidence_image_bundle_v1", "Evidence Image Bundle V1"),
]

EXPORT_TARGET_OBJECT_TYPE_SELECTION = [
    ("batch", "Batch"),
    ("waybill", "Waybill"),
    ("evidence", "Evidence"),
    ("customer", "Customer"),
    ("partner", "Partner"),
    ("product", "Product"),
]

EXPORT_TASK_STATUS_SELECTION = [
    ("pending", "Pending"),
    ("running", "Running"),
    ("success", "Success"),
    ("partial_failed", "Partial Failed"),
    ("failed", "Failed"),
    ("expired", "Expired"),
    ("cancelled", "Cancelled"),
]

EXPORT_TASK_LINE_STATUS_SELECTION = [
    ("pending", "Pending"),
    ("success", "Success"),
    ("failed", "Failed"),
    ("skipped", "Skipped"),
]

EXPORT_ERROR_STAGE_SELECTION = [
    ("scope_validate", "Scope Validate"),
    ("target_resolve", "Target Resolve"),
    ("data_collect", "Data Collect"),
    ("workbook_build", "Workbook Build"),
    ("file_store", "File Store"),
    ("download_prepare", "Download Prepare"),
]
