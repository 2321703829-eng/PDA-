from odoo import http
from odoo.addons.web.controllers.home import Home
from odoo.http import request
from odoo.tools import config

try:
    from odoo.addons.auth_signup.controllers.main import AuthSignupHome
except ImportError:
    AuthSignupHome = None


class _TenantHostDbGuardMixin:
    """Force public auth routes to trust the Host-matched tenant db, not an external db query param."""

    def _get_host_matched_db(self):
        if config["list_db"]:
            return None
        matched = http.db_list(force=True)
        if len(matched) == 1:
            return matched[0]
        return None

    def _force_host_db(self):
        host_db = self._get_host_matched_db()
        if not host_db:
            return None
        request.params["db"] = host_db
        if request.session.db != host_db:
            request.session.db = host_db
        return host_db


class LogisticsWebTenantAwareHome(_TenantHostDbGuardMixin, Home):

    @http.route()
    def web_client(self, s_action=None, **kw):
        self._force_host_db()
        return super().web_client(s_action=s_action, **kw)

    @http.route()
    def web_login(self, redirect=None, **kw):
        self._force_host_db()
        return super().web_login(redirect=redirect, **kw)


if AuthSignupHome:

    class LogisticsWebTenantAwareAuthSignupHome(_TenantHostDbGuardMixin, AuthSignupHome):

        @http.route()
        def web_login(self, *args, **kw):
            self._force_host_db()
            return super().web_login(*args, **kw)

        @http.route()
        def web_auth_signup(self, *args, **kw):
            self._force_host_db()
            return super().web_auth_signup(*args, **kw)

        @http.route()
        def web_auth_reset_password(self, *args, **kw):
            self._force_host_db()
            return super().web_auth_reset_password(*args, **kw)
