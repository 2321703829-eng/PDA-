from odoo import SUPERUSER_ID, api


def post_init_hook(env_or_cr, registry=None):
    if registry is None:
        env = env_or_cr
    else:
        env = api.Environment(env_or_cr, SUPERUSER_ID, {})
    evidence_model = env["logistics.trace.evidence"].sudo()
    evidence_model._migrate_legacy_images_to_subtable()
    evidence_model._refresh_legacy_fallback_state()
