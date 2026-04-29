/** @odoo-module */

import { Component } from "@odoo/owl";

export class SummaryBand extends Component {
    static template = "logistics_web.SummaryBand";
    static props = {
        items: { type: Array, optional: true },
    };
}
