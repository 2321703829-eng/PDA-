import json

from odoo import http
from odoo.http import request


AMAP_KEY = "f3d2d7ffa1a949b52d4735a6f014c871"


class TmsRouteMapController(http.Controller):
    @http.route("/tms/route/<int:batch_id>/map", type="http", auth="user", website=False)
    def route_map(self, batch_id, **kwargs):
        batch = request.env["logistics.route.planning.batch"].browse(batch_id).exists()
        if not batch:
            return request.not_found()

        stops = []
        for stop in batch.stop_line_ids.sorted(key=lambda s: s.stop_seq):
            lon = stop.longitude
            lat = stop.latitude
            if not lon or not lat:
                continue
            stops.append({
                "sequence": stop.stop_seq,
                "name": stop.store_name or "",
                "address": stop.address_detail or "",
                "lng": float(lon),
                "lat": float(lat),
                "waybill": stop.waybill_no or "",
            })

        payload = json.dumps({
            "batch": batch.batch_no or batch.display_name,
            "status": batch.route_status or "",
            "stops": stops,
        }, ensure_ascii=False).replace("</", "<\\/")

        return request.make_response(self._render_html(payload),
            headers=[("Content-Type", "text/html; charset=utf-8")])

    def _render_html(self, payload):
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>路线地图</title>
  <style>
    html, body, #map {{ width: 100%; height: 100%; margin: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .panel {{
      position: absolute; left: 24px; top: 24px; z-index: 10; width: 320px;
      max-height: calc(100% - 48px); overflow: auto;
      background: rgba(255,255,255,.94); border: 1px solid #d9e2ef;
      box-shadow: 0 20px 50px rgba(15,23,42,.16); border-radius: 8px;
    }}
    .panel header {{ padding: 14px 18px 10px; border-bottom: 1px solid #e5edf7; }}
    .panel h1 {{ margin: 0 0 4px; font-size: 16px; }}
    .panel p {{ margin: 0; color: #64748b; font-size: 13px; }}
    .stop {{ padding: 10px 18px; border-bottom: 1px solid #eef2f7; cursor: pointer; }}
    .stop:hover {{ background: #f0f4ff; }}
    .stop-title {{ font-weight: 700; font-size: 14px; }}
    .stop-meta {{ color: #64748b; font-size: 12px; }}
    .empty {{ padding: 18px; color: #b91c1c; font-weight: 700; }}
  </style>
  <script src="https://webapi.amap.com/maps?v=2.0&key={AMAP_KEY}"></script>
</head>
<body>
  <div id="map"></div>
  <aside class="panel">
    <header><h1 id="batch-title">路线地图</h1><p id="batch-summary"></p></header>
    <div id="stop-list"></div>
  </aside>
  <script>
    const data = {payload};
    const map = new AMap.Map("map", {{
      resizeEnable: true, zoom: 11,
      center: data.stops.length ? [data.stops[0].lng, data.stops[0].lat] : [113.53, 23.08],
      viewMode: "2D"
    }});
    document.getElementById("batch-title").textContent = data.batch || "路线地图";
    document.getElementById("batch-summary").textContent = "状态：" + (data.status || "-") + " | 站点：" + data.stops.length;
    const list = document.getElementById("stop-list");
    if (!data.stops.length) {{
      list.innerHTML = '<div class="empty">此批次没有经纬度坐标，请在排线完成后重新导入。</div>';
    }} else {{
      const path = [];
      data.stops.forEach(function(stop) {{
        const pos = [stop.lng, stop.lat];
        path.push(pos);
        new AMap.Marker({{
          position: pos, label: {{ content: String(stop.sequence), direction: "top" }}, title: stop.name, map: map
        }}).on("click", function() {{
          new AMap.InfoWindow({{ content: "<b>" + stop.sequence + ". " + stop.name + "</b><br/>" + (stop.address || "") + "<br/>" + (stop.waybill || "") }}).open(map, pos);
        }});
        const div = document.createElement("div");
        div.className = "stop";
        div.innerHTML = '<div class="stop-title">' + stop.sequence + '. ' + stop.name + '</div><div class="stop-meta">' + (stop.address || "") + '</div><div class="stop-meta">运单: ' + (stop.waybill || "-") + '</div>';
        div.onclick = function() {{ map.setCenter(pos); map.setZoom(15); }};
        list.appendChild(div);
      }});
      if (path.length > 1) {{
        new AMap.Polyline({{ path: path, strokeColor: "#1d4ed8", strokeWeight: 5, strokeOpacity: .85, lineJoin: "round", map: map }});
      }}
      map.setFitView();
    }}
  </script>
</body>
</html>"""
