/** @odoo-module */

import { BaseImportModel } from "@base_import/import_model";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(BaseImportModel.prototype, {
    _getCSVFormattingOptions() {
        const options = super._getCSVFormattingOptions(...arguments);
        options.date_format.label = _t("日期格式：");
        options.datetime_format.label = _t("日期时间格式：");
        return options;
    },
});
