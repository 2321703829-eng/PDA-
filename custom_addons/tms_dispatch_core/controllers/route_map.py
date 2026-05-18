import json
from odoo import http
from odoo.http import request


class RouteMapController(http.Controller):

    @http.route("/tms/route/<int:batch_id>/map", type="http", auth="user", website=False)
    def route_map(self, batch_id, **kw):
        batch = request.env["logistics.route.planning.batch"].sudo().browse(batch_id)
        if not batch.exists():
            return request.not_found()

        stops = []
        for line in batch.stop_line_ids.sorted("stop_seq"):
            if line.longitude and line.latitude:
                stops.append({
                    "name": line.store_name or "",
                    "lng": line.longitude,
                    "lat": line.latitude,
                    "seq": line.stop_seq,
                    "address": line.address_detail or "",
                    "waybill_no": line.waybill_no or "",
                })

        amap_key = "f3d2d7ffa1a949b52d4735a6f014c871"
        stops_json = json.dumps(stops, ensure_ascii=False)

        html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>排线地图 - {batch.batch_no}</title>
<style>
  html,body,#map{{height:100%;margin:0;padding:0}}
  #info{{position:absolute;top:10px;right:10px;z-index:999;background:rgba(255,255,255,.93);padding:12px 16px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.15);font-size:14px;max-width:320px}}
  #info h4{{margin:0 0 8px 0;font-size:16px}}
  #info p{{margin:2px 0;color:#555}}
  .stop-item{{cursor:pointer;padding:4px 6px;border-radius:4px}}
  .stop-item:hover{{background:#e8f0fe}}
  .stop-item.active{{background:#d2e3fc;font-weight:bold}}
</style>
</head>
<body>
<div id="info">
  <h4>{batch.batch_no}</h4>
  <p>车辆: {batch.vehicle_no or ''} | 司机: {batch.driver_name or ''}</p>
  <p>站点数: {len(stops)} | 状态: {batch.route_status or ''}</p>
  <hr style="margin:8px 0"/>
  <div id="stopList" style="max-height:40vh;overflow:auto"></div>
</div>
<div id="map"></div>
<script src="https://webapi.amap.com/maps?v=2.0&key={amap_key}"></script>
<script>
var stops = {stops_json};
var map = new AMap.Map('map', {{ zoom: 11, center: stops.length ? [stops[0].lng, stops[0].lat] : [113.53, 23.08] }});
var markers = [];
var path = stops.map(function(s) {{ return [s.lng, s.lat]; }});

// Draw route line
if (path.length > 1) {{
  new AMap.Polyline({{ path: path, strokeColor: '#1a56db', strokeWeight: 4, strokeOpacity: .7, showDir: true }}).setMap(map);
}}

// Draw markers
stops.forEach(function(s, i) {{
  var marker = new AMap.Marker({{
    position: [s.lng, s.lat],
    title: s.name,
    label: {{ content: String(i+1), offset: new AMap.Pixel(0,-5) }},
    map: map
  }});
  marker.on('click', function() {{ highlightStop(i); }});
  markers.push(marker);
  map.setFitView();
}});

// Build stop list
var list = document.getElementById('stopList');
stops.forEach(function(s, i) {{
  var div = document.createElement('div');
  div.className = 'stop-item';
  div.id = 'stop-' + i;
  div.innerHTML = '<b>' + (i+1) + '.</b> ' + s.name + ' <span style=color:#999;font-size:12px>' + (s.waybill_no || '') + '</span>';
  div.onclick = function() {{ highlightStop(i); map.setCenter([s.lng, s.lat]); map.setZoom(15); }};
  list.appendChild(div);
}});

function highlightStop(i) {{
  document.querySelectorAll('.stop-item').forEach(function(el) {{ el.classList.remove('active'); }});
  var el = document.getElementById('stop-' + i);
  if (el) el.classList.add('active');
}}
</script>
</body>
</html>"""
        return request.make_response(html, headers=[("Content-Type", "text/html; charset=utf-8")])
