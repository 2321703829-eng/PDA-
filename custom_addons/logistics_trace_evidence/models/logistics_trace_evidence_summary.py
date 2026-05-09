from markupsafe import escape

from odoo import fields, models, tools
from odoo.exceptions import UserError


class LogisticsTraceEvidenceSummary(models.Model):
    _name = "logistics.trace.evidence.summary"
    _description = "留痕证据汇总"
    _auto = False
    _order = "latest_uploaded_at desc, evidence_count desc, id desc"
    _rec_name = "waybill_no"

    waybill_id = fields.Many2one("logistics.dispatch.waybill", string="运单", readonly=True)
    waybill_no = fields.Char(string="运单号", readonly=True)
    batch_id = fields.Many2one("logistics.dispatch.batch", string="批次", readonly=True)
    batch_display_text = fields.Char(string="批次号", readonly=True)
    store_names_text = fields.Text(string="门店名称", readonly=True)
    contact_phones_text = fields.Text(string="门店联系电话", readonly=True)
    trace_event_count = fields.Integer(string="留痕数量", readonly=True)
    evidence_count = fields.Integer(string="证据数量", readonly=True)
    latest_uploaded_at = fields.Datetime(string="最新上传时间", readonly=True)
    upload_role = fields.Selection(
        [
            ("warehouse", "仓库留痕"),
            ("driver", "司机留痕"),
            ("unknown", "未标记"),
        ],
        string="留痕端",
        readonly=True,
    )
    preview_urls_text = fields.Text(string="预览地址列表", readonly=True)
    thumbnail_html = fields.Html(
        string="证据缩略图",
        compute="_compute_thumbnail_html",
        sanitize=False,
        readonly=True,
    )

    gallery_html = fields.Html(
        string="Evidence Gallery",
        compute="_compute_gallery_html",
        sanitize=False,
        readonly=True,
    )

    def _split_preview_urls(self):
        self.ensure_one()
        return [url.strip() for url in (self.preview_urls_text or "").splitlines() if url.strip()]

    def _build_gallery_html(self, urls, *, limit=None, show_more=False, zoom=False):
        visible_urls = urls if limit is None else urls[:limit]
        if not visible_urls:
            return '<span style="color:#6b7280;">No images</span>'

        items = []
        for index, url in enumerate(visible_urls, start=1):
            safe_url = escape(url)
            if not zoom:
                items.append(
                    (
                        '<span title="Evidence image {index}" '
                        'style="display:inline-flex;width:62px;height:62px;border-radius:10px;'
                        'overflow:hidden;border:1px solid #d1d5db;background:#f8fafc;">'
                        '<img src="{url}" alt="Evidence image {index}" '
                        'style="width:100%;height:100%;object-fit:cover;display:block;"/>'
                        "</span>"
                    ).format(url=safe_url, index=index)
                )
                continue

            items.append(
                (
                    '<details class="o_evidence_zoom" name="o_evidence_zoom" '
                    'style="position:relative;display:inline-flex;">'
                    '<summary title="Click to enlarge" '
                    'style="list-style:none;display:inline-flex;width:62px;height:62px;border-radius:10px;'
                    'overflow:hidden;border:1px solid #d1d5db;background:#f8fafc;cursor:zoom-in;">'
                    '<img src="{url}" alt="Evidence image {index}" '
                    'style="width:100%;height:100%;object-fit:cover;display:block;"/>'
                    "</summary>"
                    '<div style="position:fixed;left:50%;bottom:28px;transform:translateX(-50%);z-index:10000;'
                    'padding:12px;border-radius:14px;background:#fff;border:1px solid #d1d5db;'
                    'box-shadow:0 18px 50px rgba(15,23,42,0.22);">'
                    '<img src="{url}" alt="Evidence image {index} preview" '
                    'style="display:block;max-width:min(960px,86vw);max-height:76vh;object-fit:contain;"/>'
                    '<div style="font-size:12px;color:#6b7280;margin-top:8px;">Click thumbnail again to close</div>'
                    "</div>"
                    "</details>"
                ).format(url=safe_url, index=index)
            )
        more_count = max(len(urls) - len(visible_urls), 0) if show_more else 0
        if more_count:
            items.append(
                (
                    '<span title="Open detail page to view all images" '
                    'style="display:inline-flex;align-items:center;justify-content:center;'
                    'min-width:62px;height:62px;padding:0 10px;border-radius:10px;'
                    'background:#eef2ff;color:#4338ca;font-weight:600;">+{count}</span>'
                ).format(count=more_count)
            )

        return (
            '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;max-width:720px;">'
            + "".join(items)
            + "</div>"
        )

    def _compute_thumbnail_html(self):
        for record in self:
            urls = record._split_preview_urls()
            record.thumbnail_html = record._build_gallery_html(urls, limit=6, show_more=True, zoom=False)

    def _compute_gallery_html(self):
        for record in self:
            urls = record._split_preview_urls()
            record.gallery_html = record._build_gallery_html(urls, limit=None, show_more=False, zoom=True)

    def action_open_waybill_evidences(self):
        self.ensure_one()
        domain = []
        if self.waybill_id:
            domain.append(("waybill_id", "=", self.waybill_id.id))
        else:
            domain.append(("id", "=", 0))
        if self.upload_role:
            domain.append(("upload_role", "=", self.upload_role))

        return {
            "type": "ir.actions.act_window",
            "name": "证据明细 - %s" % (self.waybill_no or "运单"),
            "res_model": "logistics.trace.evidence",
            "views": [[False, "list"], [False, "form"]],
            "domain": domain,
            "context": {
                "search_default_group_trace": 1,
                "default_waybill_id": self.waybill_id.id if self.waybill_id else False,
            },
        }

    def action_back_to_summary_list(self):
        self.ensure_one()
        action_xml_id = "logistics_trace_evidence.action_logistics_trace_evidence_summary"
        if self.upload_role == "warehouse":
            action_xml_id = "logistics_trace_evidence.action_logistics_trace_evidence_summary_warehouse"
        elif self.upload_role == "driver":
            action_xml_id = "logistics_trace_evidence.action_logistics_trace_evidence_summary_driver"
        action = self.env["ir.actions.actions"]._for_xml_id(action_xml_id)
        action["target"] = "current"
        return action

    def action_download_waybill_images(self):
        self.ensure_one()
        if not self.waybill_id or not self.evidence_count:
            raise UserError("当前运单暂无可下载的证据图片。")
        url = "/logistics_trace/waybills/%s/evidences/download?upload_role=%s" % (
            self.waybill_id.id,
            self.upload_role or "unknown",
        )
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def action_open_waybill_record(self):
        self.ensure_one()
        if not self.waybill_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": self.waybill_no or "运单",
            "res_model": "logistics.dispatch.waybill",
            "res_id": self.waybill_id.id,
            "views": [[False, "form"]],
        }

    def action_logistics_delete(self):
        evidence_model = self.env["logistics.trace.evidence"].sudo()
        for record in self:
            if not record.waybill_id:
                continue
            domain = [("waybill_id", "=", record.waybill_id.id)]
            if record.upload_role:
                domain.append(("upload_role", "=", record.upload_role))
            evidences = evidence_model.search(domain)
            if evidences:
                evidences.action_logistics_delete()
        return True

    def action_logistics_archive(self):
        return self.action_logistics_delete()

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                WITH evidence_enriched AS (
                    SELECT
                        e.id,
                        e.waybill_id,
                        w.name AS waybill_no,
                        e.batch_id,
                        batch.name AS batch_name,
                        e.trace_event_id,
                        e.uploaded_at,
                        COALESCE(e.upload_role, 'unknown') AS upload_role,
                        COALESCE(
                            CASE
                                WHEN e.image_access_key IS NOT NULL AND e.image_access_key != ''
                                THEN '/logistics_trace/evidence-images/' || e.image_access_key
                                ELSE NULL
                            END,
                            NULLIF(e.preview_url, ''),
                            NULLIF(e.full_url, '')
                        ) AS preview_url
                    FROM logistics_trace_evidence e
                    LEFT JOIN logistics_dispatch_waybill w ON w.id = e.waybill_id
                    LEFT JOIN logistics_dispatch_batch batch ON batch.id = e.batch_id
                    WHERE e.waybill_id IS NOT NULL
                )
                SELECT
                    MIN(id) AS id,
                    waybill_id,
                    COALESCE(waybill_no, '未关联运单') AS waybill_no,
                    batch_id,
                    COALESCE(NULLIF(BTRIM(batch_name), ''), COALESCE(waybill_no, '未关联运单')) AS batch_display_text,
                    ''::text AS store_names_text,
                    ''::text AS contact_phones_text,
                    upload_role,
                    COUNT(DISTINCT trace_event_id)::integer AS trace_event_count,
                    COUNT(id)::integer AS evidence_count,
                    MAX(uploaded_at) AS latest_uploaded_at,
                    STRING_AGG(
                        preview_url,
                        E'\n'
                        ORDER BY uploaded_at DESC NULLS LAST, id DESC
                    ) FILTER (WHERE preview_url IS NOT NULL AND preview_url != '') AS preview_urls_text
                FROM evidence_enriched
                GROUP BY
                    waybill_id,
                    COALESCE(waybill_no, '未关联运单'),
                    batch_id,
                    COALESCE(NULLIF(BTRIM(batch_name), ''), COALESCE(waybill_no, '未关联运单')),
                    upload_role
            )
            """
        )
