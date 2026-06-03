from odoo import http
from odoo.addons.web.controllers.database import Database
from odoo.http import request
from odoo.tools import config


class LogisticsWebDatabaseGuard(Database):
    """Close public database-management entrypoints when list_db is disabled.

    Keep normal development behavior unchanged when list_db stays enabled.
    """

    def _database_http_closed_response(self):
        return request.make_response("Not Found", status=404)

    def _ensure_database_entry_open(self):
        if config["list_db"]:
            return
        return self._database_http_closed_response()

    @http.route("/web/database/selector", type="http", auth="none")
    def selector(self, **kw):
        if not config["list_db"]:
            if request.db and getattr(request, "env", None):
                request.env.cr.close()
                return request.redirect("/web/login")
            return self._database_http_closed_response()
        return super().selector(**kw)

    @http.route("/web/database/manager", type="http", auth="none")
    def manager(self, **kw):
        closed = self._ensure_database_entry_open()
        if closed:
            return closed
        return super().manager(**kw)

    @http.route("/web/database/list", type="jsonrpc", auth="none")
    def list(self):
        self._ensure_database_entry_open()
        return super().list()

    @http.route("/web/database/create", type="http", auth="none", methods=["POST"], csrf=False)
    def create(self, master_pwd, name, lang, password, **post):
        closed = self._ensure_database_entry_open()
        if closed:
            return closed
        return super().create(master_pwd, name, lang, password, **post)

    @http.route("/web/database/duplicate", type="http", auth="none", methods=["POST"], csrf=False)
    def duplicate(self, master_pwd, name, new_name, neutralize_database=False):
        closed = self._ensure_database_entry_open()
        if closed:
            return closed
        return super().duplicate(master_pwd, name, new_name, neutralize_database=neutralize_database)

    @http.route("/web/database/drop", type="http", auth="none", methods=["POST"], csrf=False)
    def drop(self, master_pwd, name):
        closed = self._ensure_database_entry_open()
        if closed:
            return closed
        return super().drop(master_pwd, name)

    @http.route("/web/database/backup", type="http", auth="none", methods=["POST"], csrf=False)
    def backup(self, master_pwd, name, backup_format="zip", filestore=True):
        closed = self._ensure_database_entry_open()
        if closed:
            return closed
        return super().backup(master_pwd, name, backup_format=backup_format, filestore=filestore)

    @http.route("/web/database/restore", type="http", auth="none", methods=["POST"], csrf=False, max_content_length=None)
    def restore(self, master_pwd, backup_file, name, copy=False, neutralize_database=False):
        closed = self._ensure_database_entry_open()
        if closed:
            return closed
        return super().restore(
            master_pwd,
            backup_file,
            name,
            copy=copy,
            neutralize_database=neutralize_database,
        )

    @http.route("/web/database/change_password", type="http", auth="none", methods=["POST"], csrf=False)
    def change_password(self, master_pwd, master_pwd_new):
        closed = self._ensure_database_entry_open()
        if closed:
            return closed
        return super().change_password(master_pwd, master_pwd_new)
