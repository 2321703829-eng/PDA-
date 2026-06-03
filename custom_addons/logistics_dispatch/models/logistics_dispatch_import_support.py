from odoo import api, models


def _standard_import_templates(env):
    return [
        {
            "label": env._("下载标准模板（英文列头）"),
            "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V3&template_version=v3&template_locale=en_US",
        },
        {
            "label": env._("下载标准模板（中文列头）"),
            "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V3&template_version=v3&template_locale=zh_CN",
        },
    ]


class LogisticsDispatchWaybillImportSupport(models.Model):
    _inherit = "logistics.dispatch.waybill"

    @api.model
    def get_import_templates(self):
        return _standard_import_templates(self.env)


class LogisticsDispatchWaybillCustomerLineImportSupport(models.Model):
    _inherit = "logistics.dispatch.waybill.customer.line"

    @api.model
    def get_import_templates(self):
        return _standard_import_templates(self.env)


class LogisticsDispatchWaybillCustomerGoodsLineImportSupport(models.Model):
    _inherit = "logistics.dispatch.waybill.customer.goods.line"

    @api.model
    def get_import_templates(self):
        return _standard_import_templates(self.env)
