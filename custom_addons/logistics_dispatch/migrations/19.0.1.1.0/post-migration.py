def _create_index_if_missing(cr, name, table, columns):
    cr.execute(
        """
        SELECT 1
          FROM pg_indexes
         WHERE schemaname = current_schema()
           AND indexname = %s
        """,
        (name,),
    )
    if not cr.fetchone():
        cr.execute(f"CREATE INDEX {name} ON {table} {columns}")


def migrate(cr, version):
    _create_index_if_missing(
        cr,
        "idx_waybill_batch_delivery",
        "logistics_dispatch_waybill",
        "(batch_id, delivery_date)",
    )
    _create_index_if_missing(
        cr,
        "idx_customer_line_waybill_stop",
        "logistics_dispatch_waybill_customer_line",
        "(waybill_id, stop_seq_in_waybill)",
    )
    _create_index_if_missing(
        cr,
        "idx_order_line_customer_doc",
        "logistics_dispatch_waybill_order_line",
        "(customer_line_id, doc_date)",
    )
    _create_index_if_missing(
        cr,
        "idx_goods_line_order_product",
        "logistics_dispatch_waybill_customer_goods_line",
        "(order_line_id, external_product_code_snapshot)",
    )
    _create_index_if_missing(
        cr,
        "idx_import_task_file_type_status",
        "import_task",
        "(source_file_id, object_type, status)",
    )
    _create_index_if_missing(
        cr,
        "idx_import_task_line_task_status",
        "import_task_line",
        "(task_id, status, source_row_no)",
    )
    _create_index_if_missing(
        cr,
        "idx_import_error_task_row",
        "import_error_line",
        "(task_id, source_row_no)",
    )
    _create_index_if_missing(
        cr,
        "idx_export_task_scope_type_status",
        "export_task",
        "(source_scope_id, object_type, status)",
    )
    _create_index_if_missing(
        cr,
        "idx_export_task_entry_status",
        "export_task",
        "(entry_type, status, expires_at)",
    )
    _create_index_if_missing(
        cr,
        "idx_export_task_object_entry_status",
        "export_task",
        "(object_type, entry_type, status, expires_at)",
    )
    _create_index_if_missing(
        cr,
        "idx_export_task_line_task_status",
        "export_task_line",
        "(task_id, status, target_res_id)",
    )
    _create_index_if_missing(
        cr,
        "idx_export_task_line_target_object",
        "export_task_line",
        "(task_id, target_object_type, target_res_id)",
    )
    _create_index_if_missing(
        cr,
        "idx_export_error_task_stage",
        "export_error_line",
        "(task_id, error_stage, id)",
    )
