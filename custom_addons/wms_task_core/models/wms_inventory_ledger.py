# -*- coding: utf-8 -*-
from odoo import fields, models, tools


class WmsInventoryLedger(models.Model):
    _name = "wms.inventory.ledger"
    _description = "WMS Inventory Ledger"
    _auto = False
    _order = "warehouse_id, location_id, product_id, lot_id"

    company_id = fields.Many2one("res.company", string="公司", readonly=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="仓库", readonly=True)
    location_id = fields.Many2one("stock.location", string="库位", readonly=True)
    product_id = fields.Many2one("product.product", string="产品", readonly=True)
    product_tmpl_id = fields.Many2one("product.template", string="产品模板", readonly=True)
    product_uom_id = fields.Many2one("uom.uom", string="单位", readonly=True)
    lot_id = fields.Many2one("stock.lot", string="批次/序列号", readonly=True)
    quantity_on_hand = fields.Float(string="现存数量", digits=(16, 4), readonly=True)
    reserved_quantity = fields.Float(string="预留数量", digits=(16, 4), readonly=True)
    available_quantity = fields.Float(string="可用数量", digits=(16, 4), readonly=True)
    quant_count = fields.Integer(string="库存行数", readonly=True)
    last_count_date = fields.Date(string="最近入库日期", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW wms_inventory_ledger AS (
                SELECT
                    MIN(q.id) AS id,
                    COALESCE(q.company_id, l.company_id) AS company_id,
                    w.id AS warehouse_id,
                    q.location_id AS location_id,
                    q.product_id AS product_id,
                    p.product_tmpl_id AS product_tmpl_id,
                    pt.uom_id AS product_uom_id,
                    q.lot_id AS lot_id,
                    SUM(q.quantity) AS quantity_on_hand,
                    SUM(COALESCE(q.reserved_quantity, 0.0)) AS reserved_quantity,
                    SUM(q.quantity - COALESCE(q.reserved_quantity, 0.0)) AS available_quantity,
                    COUNT(q.id)::integer AS quant_count,
                    MAX(q.in_date)::date AS last_count_date
                FROM stock_quant q
                JOIN stock_location l ON l.id = q.location_id
                JOIN product_product p ON p.id = q.product_id
                JOIN product_template pt ON pt.id = p.product_tmpl_id
                LEFT JOIN stock_warehouse w
                    ON (
                        l.parent_path LIKE CONCAT(w.view_location_id::text, '/%')
                        OR l.parent_path LIKE CONCAT('%/', w.view_location_id::text, '/%')
                    )
                WHERE l.usage = 'internal'
                GROUP BY
                    COALESCE(q.company_id, l.company_id),
                    w.id,
                    q.location_id,
                    q.product_id,
                    p.product_tmpl_id,
                    pt.uom_id,
                    q.lot_id
            )
            """
        )
