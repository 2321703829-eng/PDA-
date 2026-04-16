from tempfile import TemporaryDirectory
import json

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
        stop = self.env["logistics.waybill.stop"].create(
            {
                "waybill_no": "WB20260413001",
                "batch_no": "BT20260413001",
                "stop_seq": 1,
                "store_name": "XX Convenience Store",
                "address": "Guangzhou Road 1",
                "lat": 23.137588,
                "lng": 113.328755,
                "contact_list_json": json.dumps(
                    [
                        {"name": "XX Convenience Store", "phone": "13800001111"},
                        {"name": "Deputy Manager Wang", "phone": "13800002222"},
                        {"name": "Assistant Chen", "phone": "13800003333"},
                    ]
                ),
                "guide_url": "https://docs.qq.com/store-guide",
                "goods_info": "Frozen Seafood x 2 boxes",
                "driver_name": "Zhang San",
                "vehicle_no": "YUEA12345",
            }
        )
        trace = self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413001",
                "trace_type": "arrive",
                "route_sequence": 1,
                "driver_name": "Zhang San",
                "vehicle_no": "YUEA12345",
                "location_text": "Guangzhou Road 1",
            }
        )
        evidence = self.env["logistics.trace.evidence"].create(
            {
                "name": "Stop Arrive Image",
                "trace_id": trace.id,
                "evidence_type": "image",
            }
        )
        image_payload = self.storage.upload_image(
            file_name="stop-arrive.jpg",
            content=b"stop-arrive",
            content_type="image/jpeg",
        )
        image = evidence.register_uploaded_image(image_payload)

        self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413001",
                "trace_type": "sign",
                "route_sequence": 1,
            }
        )

        traces = self.env["logistics.trace.event"].search(
            [("waybill_no", "=", "WB20260413001")],
            order="route_sequence asc, occurred_at asc, id asc",
        )
        payload = controller._build_waybill_stops_payload(stop, traces)

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
        self.assertEqual(stop["goods_info"], "Frozen Seafood x 2 boxes")
        self.assertEqual(len(stop["evidence_images"]), 1)
        self.assertEqual(stop["evidence_images"][0]["image_id"], image.id)
        self.assertEqual(stop["evidence_images"][0]["evidence_id"], evidence.id)
        self.assertEqual(stop["evidence_images"][0]["trace_event_id"], trace.id)
        self.assertEqual(stop["evidence_images"][0]["image_access_key"], image.image_access_key)

    def test_build_waybill_stops_payload_supports_leave_status_chain(self):
        controller = LogisticsTraceEvidenceImageController()
        stop = self.env["logistics.waybill.stop"].create(
            {
                "waybill_no": "WB20260413002",
                "batch_no": "BT20260413002",
                "stop_seq": 1,
                "store_name": "YY Convenience Store",
                "address": "Shenzhen Road 8",
            }
        )

        self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413002",
                "trace_type": "load",
                "route_sequence": 1,
            }
        )
        traces = self.env["logistics.trace.event"].search(
            [("waybill_no", "=", "WB20260413002")],
            order="route_sequence asc, occurred_at asc, id asc",
        )
        payload = controller._build_waybill_stops_payload(stop, traces)
        self.assertEqual(payload["stops"][0]["status"], "CURRENT")

        self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413002",
                "trace_type": "leave",
                "route_sequence": 1,
            }
        )
        traces = self.env["logistics.trace.event"].search(
            [("waybill_no", "=", "WB20260413002")],
            order="route_sequence asc, occurred_at asc, id asc",
        )
        payload = controller._build_waybill_stops_payload(stop, traces)
        self.assertEqual(payload["stops"][0]["status"], "LEAVED")

        self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413002",
                "trace_type": "arrive",
                "route_sequence": 1,
            }
        )
        traces = self.env["logistics.trace.event"].search(
            [("waybill_no", "=", "WB20260413002")],
            order="route_sequence asc, occurred_at asc, id asc",
        )
        payload = controller._build_waybill_stops_payload(stop, traces)
        self.assertEqual(payload["stops"][0]["status"], "ARRIVED")

    def test_build_waybill_stops_payload_does_not_generate_extra_stop_from_location_text(self):
        controller = LogisticsTraceEvidenceImageController()
        stop = self.env["logistics.waybill.stop"].create(
            {
                "waybill_no": "WB20260413003",
                "batch_no": "BT20260413003",
                "stop_seq": 1,
                "store_name": "Only Store",
                "address": "Tianhe Road 9",
            }
        )
        self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413003",
                "trace_type": "leave",
                "route_sequence": 1,
                "location_text": "经度:113.81 纬度:23.26",
            }
        )
        self.env["logistics.trace.event"].create(
            {
                "biz_type": "waybill",
                "waybill_no": "WB20260413003",
                "trace_type": "arrive",
                "route_sequence": 1,
                "location_text": "经度:113.81 纬度:23.26",
            }
        )
        traces = self.env["logistics.trace.event"].search(
            [("waybill_no", "=", "WB20260413003")],
            order="route_sequence asc, occurred_at asc, id asc",
        )
        payload = controller._build_waybill_stops_payload(stop, traces)
        self.assertEqual(len(payload["stops"]), 1)
        self.assertEqual(payload["stops"][0]["store_name"], "Only Store")
        self.assertEqual(payload["stops"][0]["status"], "ARRIVED")
