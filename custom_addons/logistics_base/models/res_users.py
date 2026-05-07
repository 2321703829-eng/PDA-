from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def has_group(self, group_ext_id=None):
        # Some deployed custom views trigger a defensive has_group RPC with an
        # empty group id during webclient bootstrap. Returning False keeps the
        # old environment usable instead of crashing the whole UI.
        if not group_ext_id:
            return False
        return super().has_group(group_ext_id)
