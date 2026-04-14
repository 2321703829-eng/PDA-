/** @odoo-module */

import { Component } from "@odoo/owl";

export class StatusTag extends Component {
    static template = "logistics_web.StatusTag";
    static props = {
        label: { type: String, optional: true },
        tone: { type: String, optional: true },
    };
}
