/** @odoo-module */

export async function readModel(env, model, method, args = [], kwargs = {}) {
    return env.services.orm.call(model, method, args, kwargs);
}
