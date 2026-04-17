/** @odoo-module */

import { registry } from "@web/core/registry";

import { LogisticsBossTraceAction } from "./boss_trace_action_v2";
import { LogisticsDashboardAction } from "./dashboard_action_v2";
import { LogisticsHomeAction } from "./home_action";
import { LogisticsImportCenterAction } from "./import_center_action";

const actionsRegistry = registry.category("actions");

const registerAction = (key, component) => {
    if (!actionsRegistry.contains(key)) {
        actionsRegistry.add(key, component);
    }
};

registerAction("logistics_web.home", LogisticsHomeAction);
registerAction("logistics_web.dashboard", LogisticsDashboardAction);
registerAction("logistics_web.boss_trace", LogisticsBossTraceAction);
registerAction("logistics_web.import_center", LogisticsImportCenterAction);
