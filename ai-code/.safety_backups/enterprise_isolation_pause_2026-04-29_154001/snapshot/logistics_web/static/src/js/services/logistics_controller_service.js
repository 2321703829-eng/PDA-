/** @odoo-module */

export async function postJson(env, route, params = {}) {
    return env.services.rpc(route, params);
}
