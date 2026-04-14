from tempfile import TemporaryDirectory

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.logistics_trace_evidence.controllers.evidence_image_controller import (
    LogisticsTraceEvidenceImageController,
)
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

    def test_build_waybill_stops_payload_merges_contacts_and_status(self):
        controller = LogisticsTraceEvidenceImageController()
        store = self.env["res.partner"].create(
            {
                "name": "XX Convenience Store",
                "phone": "13800001111",
                "website": "https://docs.qq.com/store-guide",
                "street": "Guangzhou Road 1",
                "partner_latitude": 23.137588,
                "partner_longitude": 113.328755,
            }
        )
        self.env["res.partner"].create(
            {
                "name": "Deputy Manager Wang",
                "phone": "13800002222",
                "parent_id": store.id,
                "type": "contact",
            }
        )
        self.env["res.partner"].create(
            {
                "name": "Assistant Chen",
                "mobile": "13800003333",
                "parent_id": store.id,
                "type": "contact",
            }
        )

        self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413001",
                "batch_no": "BT20260413001",
                "trace_type": "arrive",
                "route_sequence": 1,
                "partner_id": store.id,
                "driver_name": "Zhang San",
                "vehicle_no": "YUEA12345",
                "location_text": "Guangzhou Road 1",
            }
        )
        self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413001",
                "trace_type": "sign",
                "route_sequence": 1,
                "partner_id": store.id,
            }
        )

        traces = self.env["logistics.trace.event"].search(
            [("waybill_no", "=", "WB20260413001")],
            order="route_sequence asc, occurred_at asc, id asc",
        )
        payload = controller._build_waybill_stops_payload(traces)

        self.assertEqual(payload["waybill_no"], "WB20260413001")
        self.assertEqual(payload["batch_no"], "BT20260413001")
        self.assertEqual(payload["driver_name"], "Zhang San")
        self.assertEqual(payload["vehicle_no"], "YUEA12345")
        self.assertEqual(len(payload["stops"]), 1)

        stop = payload["stops"][0]
        self.assertEqual(stop["stop_seq"], 1)
        self.assertEqual(stop["store_name"], "XX Convenience Store")
        self.assertEqual(stop["address"], "Guangzhou Road 1")
        self.assertEqual(stop["status"], "COMPLETED")
        self.assertEqual(stop["guide_url"], "https://docs.qq.com/store-guide")
        self.assertEqual(stop["contact_name"], "XX Convenience Store")
        self.assertEqual(stop["contact_phone"], "13800001111")
        self.assertEqual(len(stop["contact_list"]), 3)
        self.assertEqual(stop["contact_list"][1]["name"], "Deputy Manager Wang")

    def test_build_waybill_stops_payload_supports_leave_status_chain(self):
        controller = LogisticsTraceEvidenceImageController()
        store = self.env["res.partner"].create(
            {
                "name": "YY Convenience Store",
                "street": "Shenzhen Road 8",
            }
        )

        self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413002",
                "batch_no": "BT20260413002",
                "trace_type": "load",
                "route_sequence": 1,
                "partner_id": store.id,
            }
        )
        traces = self.env["logistics.trace.event"].search(
            [("waybill_no", "=", "WB20260413002")],
            order="route_sequence asc, occurred_at asc, id asc",
        )
        payload = controller._build_waybill_stops_payload(traces)
        self.assertEqual(payload["stops"][0]["status"], "CURRENT")

        self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413002",
                "trace_type": "leave",
                "route_sequence": 1,
                "partner_id": store.id,
            }
        )
        traces = self.env["logistics.trace.event"].search(
            [("waybill_no", "=", "WB20260413002")],
            order="route_sequence asc, occurred_at asc, id asc",
        )
        payload = controller._build_waybill_stops_payload(traces)
        self.assertEqual(payload["stops"][0]["status"], "LEAVED")

        self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413002",
                "trace_type": "arrive",
                "route_sequence": 1,
                "partner_id": store.id,
            }
        )
        traces = self.env["logistics.trace.event"].search(
            [("waybill_no", "=", "WB20260413002")],
            order="route_sequence asc, occurred_at asc, id asc",
        )
        payload = controller._build_waybill_stops_payload(traces)
        self.assertEqual(payload["stops"][0]["status"], "ARRIVED")
