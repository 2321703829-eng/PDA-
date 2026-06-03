from odoo import fields, models


class LogisticsStoreProfile(models.Model):
    _name = "logistics.store.profile"
    _description = "门店配送画像（兼容）"
    _table = "logistics_store_profile"
    _rec_name = "partner_id"

    _uniq_store_profile_partner = models.Constraint(
        "unique(partner_id)",
        "同一门店主档只能绑定一条门店配送画像。",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="关联门店主档",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one("res.company", string="公司", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one("res.currency", string="币种", related="company_id.currency_id", store=True)
    address_code = fields.Char(
        related="partner_id.logistics_store_code",
        string="地址编号",
        store=True,
        readonly=False,
    )
    external_customer_code = fields.Char(
        related="partner_id.external_customer_code",
        string="客户编号",
        store=True,
        readonly=False,
    )
    customer_name = fields.Char(
        related="partner_id.customer_name",
        string="客户名称",
        store=True,
        readonly=False,
    )
    address_full = fields.Text(
        related="partner_id.address_full",
        string="配送地址",
        store=True,
        readonly=False,
    )
    longitude = fields.Float(
        related="partner_id.partner_longitude",
        string="经度",
        store=True,
        readonly=False,
        digits=(10, 7),
    )
    latitude = fields.Float(
        related="partner_id.partner_latitude",
        string="纬度",
        store=True,
        readonly=False,
        digits=(10, 7),
    )
    address_region_json = fields.Json(
        related="partner_id.address_region_json",
        string="结构化地址",
        store=True,
        readonly=False,
    )
    delivery_window_text = fields.Text(
        related="partner_id.delivery_window_text",
        string="配送时间窗摘要",
        store=True,
        readonly=False,
    )
    receive_start_time = fields.Char(
        related="partner_id.receive_start_time",
        string="开始收货时间",
        store=True,
        readonly=False,
    )
    receive_end_time = fields.Char(
        related="partner_id.receive_end_time",
        string="截止收货时间",
        store=True,
        readonly=False,
    )
    receive_time_slots_text = fields.Text(
        related="partner_id.receive_time_slots_text",
        string="收货时间段",
        store=True,
        readonly=False,
    )
    no_receive_time_slots_text = fields.Text(
        related="partner_id.no_receive_time_slots_text",
        string="不收货时间段",
        store=True,
        readonly=False,
    )
    delivery_week_flags = fields.Char(
        related="partner_id.delivery_week_flags",
        string="周维度配送周期",
        store=True,
        readonly=False,
    )
    default_signoff_requirement = fields.Char(
        related="partner_id.default_signoff_requirement",
        string="默认签收要求",
        store=True,
        readonly=False,
    )
    delivery_access_flags = fields.Char(
        related="partner_id.delivery_access_flags",
        string="配送可达性编码串",
        store=True,
        readonly=False,
    )
    illegal_parking_flag = fields.Boolean(
        related="partner_id.illegal_parking_flag",
        string="违停",
        store=True,
        readonly=False,
    )
    free_parking_minutes = fields.Integer(
        related="partner_id.free_parking_minutes",
        string="免费停车时长",
        store=True,
        readonly=False,
    )
    parking_fee_per_hour = fields.Float(
        related="partner_id.parking_fee_per_hour",
        string="停车费/小时",
        store=True,
        readonly=False,
    )
    parking_location_text = fields.Text(
        related="partner_id.parking_location_text",
        string="停车位置",
        store=True,
        readonly=False,
    )
    parking_mode_text = fields.Text(
        related="partner_id.parking_mode_text",
        string="停车方式",
        store=True,
        readonly=False,
    )
    unload_entrance_text = fields.Text(
        related="partner_id.unload_entrance_text",
        string="卸货入口",
        store=True,
        readonly=False,
    )
    unload_location_text = fields.Text(
        related="partner_id.unload_location_text",
        string="卸货位置",
        store=True,
        readonly=False,
    )
    upstairs_floor_count = fields.Integer(
        related="partner_id.upstairs_floor_count",
        string="上楼层数",
        store=True,
        readonly=False,
    )
    basement_height_limit_text = fields.Text(
        related="partner_id.basement_height_limit_text",
        string="地库限高",
        store=True,
        readonly=False,
    )
    route_preference = fields.Char(
        related="partner_id.route_preference",
        string="线路偏好",
        store=True,
        readonly=False,
    )
    warehouse_preference = fields.Char(
        related="partner_id.warehouse_preference",
        string="仓库偏好",
        store=True,
        readonly=False,
    )
