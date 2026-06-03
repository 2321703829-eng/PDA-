/** @odoo-module */

import { Component } from "@odoo/owl";

export class PageHeader extends Component {
    static template = "logistics_web.PageHeader";
    static props = {
        title: { type: String, optional: true },
        subtitle: { type: String, optional: true },
    };
}
