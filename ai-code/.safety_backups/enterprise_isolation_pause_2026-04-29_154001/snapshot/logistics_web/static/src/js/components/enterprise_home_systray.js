/** @odoo-module */

import { Component } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class EnterpriseHomeSystray extends Component {
    static template = "logistics_web.EnterpriseHomeSystray";
    static props = {};

    setup() {
        this.actionService = useService("action");
        this.menuService = useService("menu");
    }

    async goHome() {
        const menu = this.findEnterpriseHomeMenu();
        if (menu?.id && menu?.actionID) {
            browser.location = `/web#menu_id=${menu.id}&action=${menu.actionID}`;
            return;
        }
        return this.actionService.doAction("logistics_web.action_logistics_web_home");
    }

    findEnterpriseHomeMenu() {
        const menus = this.menuService.getAll();
        return menus.find((menu) => menu.xmlid === "logistics_web.menu_logistics_web_home")
            || menus.find((menu) => menu.xmlid === "logistics_web.menu_tianshu_enterprise_root")
            || menus.find((menu) => menu.name === "首页" && menu.actionID)
            || menus.find((menu) => menu.name === "天枢科技企业系统" && menu.actionID)
            || null;
    }
}

registry.category("systray").add(
    "logistics_web.enterprise_home_systray",
    { Component: EnterpriseHomeSystray },
    { sequence: 10 }
);
