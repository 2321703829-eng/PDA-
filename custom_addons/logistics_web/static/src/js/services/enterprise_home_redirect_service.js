/** @odoo-module */

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";

const ENTERPRISE_HOME_ACTION_XMLID = "logistics_web.action_logistics_web_home";
const ENTERPRISE_HOME_MENU_XMLIDS = [
    "logistics_web.menu_logistics_web_home",
    "logistics_web.menu_tianshu_enterprise_root",
];
const REDIRECT_BLOCKING_KEYS = ["action", "menu_id", "id", "model", "view_type"];

function parseHashParams() {
    const rawHash = browser.location.hash || "";
    const normalizedHash = rawHash.startsWith("#") ? rawHash.slice(1) : rawHash;
    return new URLSearchParams(normalizedHash);
}

function shouldRedirectToEnterpriseHome() {
    const pathname = browser.location.pathname || "";
    if (!pathname.startsWith("/web")) {
        return false;
    }
    const params = parseHashParams();
    return !REDIRECT_BLOCKING_KEYS.some((key) => params.get(key));
}

function findEnterpriseHomeMenu(menuService) {
    const menus = menuService.getAll ? menuService.getAll() : [];
    return menus.find((menu) => ENTERPRISE_HOME_MENU_XMLIDS.includes(menu.xmlid) && menu.actionID) || null;
}

export const enterpriseHomeRedirectService = {
    dependencies: ["action", "menu"],
    start(env, { action, menu }) {
        const redirectToEnterpriseHome = async () => {
            if (!shouldRedirectToEnterpriseHome()) {
                return;
            }
            const homeMenu = findEnterpriseHomeMenu(menu);
            if (homeMenu?.id && homeMenu?.actionID) {
                browser.location = `/web#menu_id=${homeMenu.id}&action=${homeMenu.actionID}`;
                return;
            }
            await action.doAction(ENTERPRISE_HOME_ACTION_XMLID);
        };

        browser.setTimeout(() => {
            redirectToEnterpriseHome().catch(() => {});
        }, 0);

        return {
            redirectToEnterpriseHome,
        };
    },
};

registry.category("services").add("enterprise_home_redirect", enterpriseHomeRedirectService);
