from odoo.addons.web.controllers.webmanifest import WebManifest


class LogisticsWebManifest(WebManifest):
    def _get_webmanifest(self):
        manifest = super()._get_webmanifest()
        manifest.update(
            {
                "name": "天枢科技物流系统",
                "background_color": "#123d70",
                "theme_color": "#123d70",
            }
        )
        return manifest
