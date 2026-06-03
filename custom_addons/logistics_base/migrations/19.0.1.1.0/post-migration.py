from odoo import SUPERUSER_ID, api


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


def _sync_profile_columns_back_to_master(cr):
    cr.execute(
        """
        UPDATE res_partner AS rp
           SET is_logistics_customer = TRUE,
               is_logistics_store = TRUE,
               logistics_customer_code = COALESCE(NULLIF(rp.logistics_customer_code, ''), NULLIF(rp.logistics_store_code, ''), NULLIF(rp.external_customer_code, ''), rp.logistics_customer_code),
               logistics_store_code = COALESCE(NULLIF(rp.logistics_store_code, ''), NULLIF(rp.logistics_customer_code, ''), NULLIF(rp.external_customer_code, ''), rp.logistics_store_code),
               allow_cash_on_delivery = COALESCE(cp.allow_cash_on_delivery, rp.allow_cash_on_delivery),
               internal_counterparty_flag = COALESCE(cp.internal_counterparty_flag, rp.internal_counterparty_flag),
               invoice_type = COALESCE(NULLIF(cp.invoice_type, ''), rp.invoice_type),
               delivery_window_text = COALESCE(NULLIF(sp.delivery_window_text, ''), rp.delivery_window_text),
               receive_start_time = COALESCE(NULLIF(sp.receive_start_time, ''), rp.receive_start_time),
               receive_end_time = COALESCE(NULLIF(sp.receive_end_time, ''), rp.receive_end_time),
               receive_time_slots_text = COALESCE(NULLIF(sp.receive_time_slots_text, ''), rp.receive_time_slots_text),
               no_receive_time_slots_text = COALESCE(NULLIF(sp.no_receive_time_slots_text, ''), rp.no_receive_time_slots_text),
               delivery_week_flags = COALESCE(NULLIF(sp.delivery_week_flags, ''), rp.delivery_week_flags),
               default_signoff_requirement = COALESCE(NULLIF(sp.default_signoff_requirement, ''), rp.default_signoff_requirement),
               delivery_access_flags = COALESCE(NULLIF(sp.delivery_access_flags, ''), rp.delivery_access_flags),
               illegal_parking_flag = COALESCE(sp.illegal_parking_flag, rp.illegal_parking_flag),
               free_parking_minutes = COALESCE(sp.free_parking_minutes, rp.free_parking_minutes),
               parking_fee_per_hour = COALESCE(sp.parking_fee_per_hour, rp.parking_fee_per_hour),
               parking_location_text = COALESCE(NULLIF(sp.parking_location_text, ''), rp.parking_location_text),
               parking_mode_text = COALESCE(NULLIF(sp.parking_mode_text, ''), rp.parking_mode_text),
               unload_entrance_text = COALESCE(NULLIF(sp.unload_entrance_text, ''), rp.unload_entrance_text),
               unload_location_text = COALESCE(NULLIF(sp.unload_location_text, ''), rp.unload_location_text),
               upstairs_floor_count = COALESCE(sp.upstairs_floor_count, rp.upstairs_floor_count),
               basement_height_limit_text = COALESCE(NULLIF(sp.basement_height_limit_text, ''), rp.basement_height_limit_text),
               route_preference = COALESCE(NULLIF(sp.route_preference, ''), rp.route_preference),
               warehouse_preference = COALESCE(NULLIF(sp.warehouse_preference, ''), rp.warehouse_preference),
               address_region_json = COALESCE(sp.address_region_json, rp.address_region_json)
          FROM logistics_customer_profile AS cp
          FULL OUTER JOIN logistics_store_profile AS sp
            ON cp.partner_id = sp.partner_id
         WHERE rp.id = COALESCE(cp.partner_id, sp.partner_id)
        """
    )


def _sync_master_backed_profile_columns(cr):
    cr.execute(
        """
        UPDATE logistics_customer_profile AS p
           SET customer_level = rp.logistics_customer_level,
               customer_status = rp.customer_status,
               registered_phone = rp.contact_phone,
               registered_address = rp.address_full,
               customer_seq_no = rp.logistics_customer_code
          FROM res_partner AS rp
         WHERE p.partner_id = rp.id
        """
    )
    cr.execute(
        """
        UPDATE logistics_store_profile AS p
           SET address_code = rp.logistics_store_code,
               external_customer_code = rp.external_customer_code,
               customer_name = rp.customer_name,
               address_full = rp.address_full,
               longitude = rp.partner_longitude,
               latitude = rp.partner_latitude
          FROM res_partner AS rp
         WHERE p.partner_id = rp.id
        """
    )
    cr.execute(
        """
        UPDATE logistics_driver_profile AS p
           SET internal_driver_code = he.logistics_employee_code,
               driver_name = he.name
          FROM hr_employee AS he
         WHERE p.employee_id = he.id
        """
    )


def migrate(cr, version):
    api.Environment(cr, SUPERUSER_ID, {})
    _create_index_if_missing(cr, "idx_customer_profile_status", "logistics_customer_profile", "(customer_status)")
    _create_index_if_missing(
        cr,
        "idx_customer_profile_cod_internal",
        "logistics_customer_profile",
        "(allow_cash_on_delivery, internal_counterparty_flag)",
    )
    _create_index_if_missing(cr, "idx_store_profile_partner", "logistics_store_profile", "(partner_id)")
    _create_index_if_missing(cr, "idx_store_profile_wh_pref", "logistics_store_profile", "(warehouse_preference)")
    _create_index_if_missing(cr, "idx_product_unit_product", "logistics_product_unit", "(product_tmpl_id)")
    _create_index_if_missing(cr, "idx_driver_profile_employee", "logistics_driver_profile", "(employee_id)")
    _create_index_if_missing(cr, "idx_vehicle_profile_vehicle", "logistics_vehicle_profile", "(vehicle_id)")
    _sync_profile_columns_back_to_master(cr)
    _sync_master_backed_profile_columns(cr)
