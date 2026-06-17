from html import escape

from werkzeug.urls import url_encode

from odoo import http
from odoo.http import request


def _field_value(record, field_name):
    if field_name not in record._fields:
        return False
    return record[field_name]


class WmsBarcodeLabelController(http.Controller):
    """Browser-printable WMS barcode label page."""

    _MODEL_CONFIG = {
        "product.product": {
            "title": "商品条码",
            "code": lambda record: _field_value(record, "barcode") or _field_value(record, "default_code") or record.display_name,
            "name": lambda record: record.display_name,
            "lines": lambda record: [
                ("商品编码", _field_value(record, "default_code") or ""),
                ("单位", record.uom_id.display_name if record.uom_id else ""),
            ],
        },
        "stock.location": {
            "title": "库位条码",
            "code": lambda record: _field_value(record, "barcode") or _field_value(record, "complete_name") or record.display_name,
            "name": lambda record: _field_value(record, "complete_name") or record.display_name,
            "lines": lambda record: [
                ("库位名称", record.display_name),
                ("库位类型", _field_value(record, "usage") or ""),
            ],
        },
        "wms.outbound.task": {
            "title": "出库任务条码",
            "code": lambda record: record.name,
            "name": lambda record: record.name,
            "lines": lambda record: [
                ("仓库", record.warehouse_id.display_name if record.warehouse_id else ""),
                ("门店", record.store_partner_id.display_name if record.store_partner_id else ""),
            ],
        },
        "wms.handover.order": {
            "title": "交接单条码",
            "code": lambda record: record.name,
            "name": lambda record: record.name,
            "lines": lambda record: [
                ("仓库", record.warehouse_id.display_name if record.warehouse_id else ""),
                ("出库任务", record.outbound_task_id.name if record.outbound_task_id else ""),
            ],
        },
    }

    @http.route("/wms/barcode/label/<string:model>/<int:record_id>", type="http", auth="user")
    def print_label(self, model, record_id, **kwargs):
        config = self._MODEL_CONFIG.get(model)
        if not config:
            return request.not_found()

        record = request.env[model].browse(record_id).exists()
        if not record:
            return request.not_found()

        code = (config["code"](record) or "").strip()
        if not code:
            return request.make_response(
                self._render_message("没有可打印的条码内容"),
                headers=self._headers(),
            )

        barcode_params = url_encode(
            {
                "barcode_type": "Code128",
                "value": code,
                "width": 620,
                "height": 150,
                "humanreadable": 0,
            }
        )
        barcode_src = f"/report/barcode/?{barcode_params}"
        line_html = "".join(
            f"<div><span>{escape(label)}</span><strong>{escape(str(value or '-'))}</strong></div>"
            for label, value in config["lines"](record)
        )

        html = f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8"/>
    <meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate, max-age=0"/>
    <meta http-equiv="Pragma" content="no-cache"/>
    <title>{escape(config["title"])} - {escape(code)}</title>
    <style>
        @page {{ size: 60mm 80mm; margin: 0; }}
        * {{ box-sizing: border-box; }}
        html, body {{
            margin: 0;
            padding: 0;
            background: #f3f6fa;
            color: #172233;
            font-family: "Microsoft YaHei", Arial, sans-serif;
        }}
        .toolbar {{
            display: flex;
            gap: 8px;
            padding: 12px;
            background: #fff;
            border-bottom: 1px solid #d8e2ee;
        }}
        .toolbar button {{
            border: 1px solid #1f669e;
            background: #1f669e;
            color: #fff;
            border-radius: 6px;
            padding: 8px 14px;
            cursor: pointer;
            font-weight: 700;
        }}
        .toolbar .secondary {{
            background: #fff;
            color: #1f669e;
        }}
        .preview {{
            padding: 16px;
            min-height: calc(100vh - 57px);
            display: flex;
            align-items: flex-start;
            justify-content: center;
        }}
        .label {{
            width: 76mm;
            height: 56mm;
            padding: 3mm 4mm;
            background: #fff;
            border: 1px solid #d6e0ea;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .title {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            font-weight: 800;
            line-height: 1.1;
        }}
        .name {{
            font-size: 10px;
            font-weight: 700;
            line-height: 1.15;
            max-height: 7mm;
            overflow: hidden;
        }}
        .barcode {{
            text-align: center;
            height: 16mm;
        }}
        .barcode img {{
            width: 58mm;
            height: 16mm;
            object-fit: contain;
        }}
        .code {{
            text-align: center;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: .5px;
            line-height: 1.1;
        }}
        .meta {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 1px;
            font-size: 7px;
            line-height: 1.1;
            color: #4d5f73;
        }}
        .meta div {{
            display: flex;
            justify-content: space-between;
            gap: 4px;
            white-space: nowrap;
            overflow: hidden;
        }}
        .meta strong {{
            color: #172233;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .print-version {{
            margin-left: auto;
            color: #66788a;
            font-size: 12px;
            line-height: 32px;
        }}
        @media print {{
            @page {{ size: 60mm 80mm; margin: 0; }}
            html, body {{
                width: 60mm;
                height: 80mm;
                overflow: hidden;
                background: #fff;
            }}
            .toolbar {{
                display: none !important;
            }}
            .preview {{
                padding: 0;
                min-height: 0;
                width: 60mm;
                height: 80mm;
                display: block;
                position: relative;
                overflow: hidden;
                page-break-inside: avoid;
                break-inside: avoid;
            }}
            .label {{
                width: 56mm;
                height: 76mm;
                padding: 3mm 4mm;
                position: absolute;
                left: 50%;
                top: 50%;
                margin: 0;
                border: none;
                transform: translate(-50%, -50%) rotate(90deg);
                transform-origin: center center;
                break-after: avoid;
                page-break-after: avoid;
                overflow: hidden;
            }}
            .title {{
                font-size: 9px;
            }}
            .name {{
                font-size: 8px;
                max-height: 8mm;
            }}
            .barcode {{
                height: 16mm;
            }}
            .barcode img {{
                width: 44mm;
                height: 16mm;
            }}
            .code {{
                font-size: 10px;
            }}
            .meta {{
                font-size: 6px;
            }}
        }}
    </style>
</head>
<body>
    <div class="toolbar">
        <button onclick="window.print()">打印条码</button>
        <button class="secondary" onclick="window.close()">关闭</button>
        <span class="print-version">80×60 横向一页版 v20260616-1800</span>
    </div>
    <main class="preview">
        <section class="label">
            <div class="title">
                <span>{escape(config["title"])}</span>
                <span>WMS</span>
            </div>
            <div class="name">{escape(config["name"](record) or code)}</div>
            <div class="barcode"><img src="{escape(barcode_src)}" alt="{escape(code)}"/></div>
            <div class="code">{escape(code)}</div>
            <div class="meta">{line_html}</div>
        </section>
    </main>
</body>
</html>"""
        return request.make_response(html, headers=self._headers())

    def _headers(self):
        return [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0"),
            ("Pragma", "no-cache"),
            ("Expires", "0"),
        ]

    def _render_message(self, message):
        safe_message = escape(message)
        return f"""<!doctype html>
<html><head><meta charset="utf-8"/><title>条码打印</title></head>
<body style="font-family:Microsoft YaHei,Arial,sans-serif;padding:24px;">{safe_message}</body></html>"""
