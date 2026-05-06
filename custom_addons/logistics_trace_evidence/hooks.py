from odoo import SUPERUSER_ID, api


def post_init_hook(env_or_cr, registry=None):
    if registry is None:
        env = env_or_cr
    else:
        env = api.Environment(env_or_cr, SUPERUSER_ID, {})
    env["logistics.trace.evidence"].sudo()._migrate_legacy_images_to_subtable()
