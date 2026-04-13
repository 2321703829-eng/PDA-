from tempfile import TemporaryDirectory

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.logistics_trace_evidence.services.image_storage_service import LogisticsEvidenceImageStorage


@tagged("post_install", "-at_install")
class TestLogisticsTraceEvidence(TransactionCase):
    def setUp(self):
        super().setUp()
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.env["ir.config_parameter"].sudo().set_param(
            "logistics_trace_evidence.image_storage_root",
            self.temp_dir.name,
        )
        self.trace_event = self.env["logistics.trace.event"].create(
            {
                "name": "Waybill Arrive",
                "biz_type": "waybill",
                "waybill_no": "WB20260411001",
                "trace_type": "arrive",
            }
        )
        self.evidence = self.env["logistics.trace.evidence"].create(
            {
                "name": "Waybill Arrival Image",
                "trace_id": self.trace_event.id,
                "evidence_type": "image",
            }
        )
        self.storage = LogisticsEvidenceImageStorage(self.env)

    def test_register_uploaded_image_creates_reference_record(self):
        payload = self.storage.upload_image(
            file_name="demo.jpg",
            content=b"trace-image",
            content_type="image/jpeg",
        )

        image = self.evidence.register_uploaded_image(payload)

        self.assertEqual(image.source_filename, "demo.jpg")
        self.assertEqual(image.stored_file_name, payload["file_name"])
        self.assertEqual(image.storage_status, "active")
        self.assertEqual(image.waybill_no, "WB20260411001")
        self.assertEqual(self.evidence.image_count, 1)

    def test_action_sync_all_image_meta_updates_existing_images(self):
        payload = self.storage.upload_image(
            file_name="demo.jpg",
            content=b"trace-image-2",
            content_type="image/jpeg",
        )
        image = self.evidence.register_uploaded_image(payload)

        image.write(
            {
                "mime_type": False,
                "file_size": 0,
                "storage_status": "new",
            }
        )

        self.evidence.action_sync_all_image_meta()

        image.invalidate_recordset()
        self.assertEqual(image.mime_type, "image/jpeg")
        self.assertEqual(image.file_size, len(b"trace-image-2"))
        self.assertEqual(image.storage_status, "active")
        self.assertEqual(image.waybill_no, "WB20260411001")
