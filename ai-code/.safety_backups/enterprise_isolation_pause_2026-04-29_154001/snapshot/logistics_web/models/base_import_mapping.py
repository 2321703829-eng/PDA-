from odoo import api, models


class BaseImportMapping(models.Model):
    _inherit = "base_import.mapping"

    @api.model_create_multi
    def create(self, vals_list):
        normalized_vals_list = [self._normalize_column_name(vals) for vals in vals_list]
        return super().create(normalized_vals_list)

    def write(self, vals):
        return super().write(self._normalize_column_name(vals))

    @api.model
    def _normalize_column_name(self, vals):
        vals = dict(vals)
        column_name = vals.get("column_name")
        if isinstance(column_name, str):
            vals["column_name"] = column_name.strip().lower()
        return vals
