/** @odoo-module */

import { Component } from "@odoo/owl";

export class SummaryCard extends Component {
    static template = "logistics_web.SummaryCard";
    static props = {
        label: { type: String, optional: true },
        value: { optional: true },
    };
}
