/** @odoo-module */

import { registry } from "@web/core/registry";

const SYSTEM_TITLE = "天枢科技企业系统";

export const tianshuTitleService = {
    dependencies: ["title"],
    start(env, { title }) {
        title.setParts({ brand: SYSTEM_TITLE });
        return {};
    },
};

registry.category("services").add("tianshu_title", tianshuTitleService);
