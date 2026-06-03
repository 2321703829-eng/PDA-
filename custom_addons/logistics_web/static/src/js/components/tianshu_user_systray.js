/** @odoo-module */

import { Component, useExternalListener, useRef, useState } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";

export class TianshuUserSystray extends Component {
    static template = "logistics_web.TianshuUserSystray";
    static props = {};

    setup() {
        this.rootRef = useRef("root");
        this.state = useState({ open: false });
        useExternalListener(document, "pointerdown", (ev) => {
            const root = this.rootRef.el;
            if (this.state.open && root && !root.contains(ev.target)) {
                this.state.open = false;
            }
        });
        useExternalListener(document, "keydown", (ev) => {
            if (ev.key === "Escape") {
                this.state.open = false;
            }
        });
    }

    get initial() {
        return (user.name || "A").trim().slice(0, 1).toUpperCase() || "A";
    }

    toggleMenu() {
        this.state.open = !this.state.open;
    }

    openProfile() {
        this.state.open = false;
        browser.location.href = "/my/profile";
    }

    logout() {
        this.state.open = false;
        browser.location.href = "/web/session/logout?redirect=/";
    }
}

registry.category("systray").add(
    "logistics_web.tianshu_user_systray",
    { Component: TianshuUserSystray },
    { sequence: 90 }
);
