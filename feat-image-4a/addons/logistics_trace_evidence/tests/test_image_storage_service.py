from pathlib import Path
from tempfile import TemporaryDirectory

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.logistics_trace_evidence.services.image_storage_service import LogisticsEvidenceImageStorage


@tagged("post_install", "-at_install")
class TestLogisticsEvidenceImageStorage(TransactionCase):
    def setUp(self):
        super().setUp()
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("logistics_trace_evidence.image_public_base_url", "http://odoo.test")
        icp.set_param("logistics_trace_evidence.image_storage_root", self.temp_dir.name)
        self.storage = LogisticsEvidenceImageStorage(self.env)

    def test_build_urls(self):
        self.assertEqual(
            self.storage.build_preview_url("img_x"),
            "http://odoo.test/logistics_trace/evidence-images/img_x",
        )
        self.assertEqual(
            self.storage.build_download_url("img_x"),
            "http://odoo.test/logistics_trace/evidence-images/img_x?download=true",
        )

    def test_upload_image_writes_real_file(self):
        payload = self.storage.upload_image(
            file_name="demo.jpg",
            content=b"abc",
            content_type="image/jpeg",
        )

        self.assertTrue(payload["image_access_key"].startswith("img_"))
        self.assertEqual(payload["storage_provider"], "local")
        stored_path = Path(self.temp_dir.name) / payload["storage_relative_path"]
        self.assertTrue(stored_path.exists())
        self.assertEqual(stored_path.read_bytes(), b"abc")

    def test_read_image_returns_real_binary_content(self):
        payload = self.storage.upload_image(
            file_name="demo.jpg",
            content=b"abcdef",
            content_type="image/jpeg",
        )
        image_record = self.env["logistics.trace.evidence.image"].new(
            {
                "image_access_key": payload["image_access_key"],
                "source_filename": payload["original_file_name"],
                "stored_file_name": payload["file_name"],
                "mime_type": payload["content_type"],
                "storage_relative_path": payload["storage_relative_path"],
            }
        )

        result = self.storage.read_image(image_record)

        self.assertEqual(result["file_name"], "demo.jpg")
        self.assertEqual(result["content_type"], "image/jpeg")
        self.assertEqual(result["content_length"], 6)
        self.assertEqual(result["content"], b"abcdef")
