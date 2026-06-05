from odoo.modules.module import load_information_from_description_file
from odoo.tests.common import TransactionCase


class TestERPDocumentQueryMenu(TransactionCase):
    def test_bi_document_query_action_and_menu_are_registered(self):
        action = self.env.ref("logistics_web.action_logistics_web_erp_document_query")
        menu = self.env.ref("logistics_web.menu_enterprise_bi_erp_documents")
        bi_menu = self.env.ref("logistics_web.menu_enterprise_bi")

        self.assertEqual(action.tag, "logistics_web.erp_document_query")
        self.assertEqual(menu.parent_id, bi_menu)
        self.assertEqual(menu.action, action)

    def test_document_query_assets_are_declared(self):
        manifest = load_information_from_description_file("logistics_web")
        backend_assets = manifest["assets"]["web.assets_backend"]

        self.assertIn("logistics_web/static/src/js/actions/erp_document_query_action.js", backend_assets)
        self.assertIn("logistics_web/static/src/xml/erp_document_query_templates.xml", backend_assets)
