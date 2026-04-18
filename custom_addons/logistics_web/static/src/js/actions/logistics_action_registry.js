/** @odoo-module */

// Action modules self-register, but they still need an import chain so Odoo's
// frontend module loader actually executes them inside the backend bundle.
import "./home_action";
import "./dashboard_action_v2";
import "./boss_trace_action_v2";
import "./import_center_action";
import "./import_result_action";
import "./driver_management_action_v2";
import "./stats_center_action";
