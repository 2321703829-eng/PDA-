import json
import os

from odoo import http
from odoo.http import request


AMAP_KEY = "f3d2d7ffa1a949b52d4735a6f014c871"
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "route_planner_template.html")


class TmsRouteMapController(http.Controller):

    @http.route("/tms/route/<int:batch_id>/map", type="http", auth="user", website=False)
    def route_map(self, batch_id, **kwargs):
        batch = request.env["logistics.route.planning.batch"].browse(batch_id).exists()
        if not batch:
            return request.not_found()

        # 从站点线构建 routeData
        routes = []
        if batch.stop_line_ids:
            stops = batch.stop_line_ids.sorted(key=lambda s: s.stop_seq)
            points = []
            for s in stops:
                points.append({
                    "seq": s.stop_seq,
                    "name": s.store_name or "",
                    "site_id": s.waybill_no or "",
                    "address": s.address_detail or "",
                    "lng": float(s.longitude) if s.longitude else 0,
                    "lat": float(s.latitude) if s.latitude else 0,
                    "weight": str(s.goods_weight_total or 0),
                    "volume": str(s.goods_volume_total or 0),
                    "piece_count": str(int(s.package_count_total or 0)),
                    "whole_piece_count": int(s.package_count_total or 0),
                    "loose_piece_count": 0,
                    "pallet_count": "0",
                    "start_receive_time": "0",
                    "end_receive_time": "0",
                    "segment_distance_km": 0,
                    "segment_duration_min": 0,
                    "eta_duration_min": 0,
                })
            if points:
                routes.append({
                    "vehicle_id": batch.vehicle_no or str(batch.id),
                    "line_no": 1,
                    "start_name": batch.vehicle_no or str(batch.id),
                    "color": "#2f54eb",
                    "start": [113.53, 23.08],
                    "points": points,
                })

        route_json = json.dumps(routes, ensure_ascii=False)

        if os.path.exists(TEMPLATE_PATH):
            with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            html = self._fallback_html(route_json)

        html = html.replace("__ROUTE_DATA_PLACEHOLDER__", route_json)
        html = html.replace('src="https://webapi.amap.com/maps?v=2.0&key=', f'src="https://webapi.amap.com/maps?v=2.0&key={AMAP_KEY}')
        return request.make_response(html, headers=[("Content-Type", "text/html; charset=utf-8")])

    def _fallback_html(self, route_json):
        return f"""<!doctype html><html><head><meta charset="utf-8"/></head>
<body><div id="map" style="width:100%;height:100%"></div>
<script src="https://webapi.amap.com/maps?v=2.0&key={AMAP_KEY}"></script>
<script>var routeData={route_json};console.log('Routes:',routeData.length);</script></body></html>"""
