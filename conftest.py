"""conftest.py — mock odoo 框架，使单测可脱离数据库用 pytest 运行。"""

import importlib
import importlib.abc
import importlib.util
import os
import sys
from types import ModuleType

ROOT = os.path.dirname(os.path.abspath(__file__))
ADDONS_PATH = os.path.join(ROOT, "custom_addons")

# ── 1. Mock odoo package ────────────────────────────────────────────

_odoo = ModuleType("odoo")
_odoo._ = lambda x: x
_odoo.SUPERUSER_ID = 1

# odoo.api
_api = ModuleType("odoo.api")

def _deco_factory(*args, **kw):
    if args and callable(args[0]):
        return args[0]
    return lambda f: f

_api.model = _deco_factory
_api.model_create_multi = _deco_factory
_api.depends = lambda *a: lambda f: f
_api.constrains = lambda *a: lambda f: f
_api.onchange = lambda *a: lambda f: f
_odoo.api = _api

# odoo.fields
_fields = ModuleType("odoo.fields")

class _FieldDescriptor:
    def __init__(self, *a, **kw):
        self.string = kw.get("string", "")
    def __set_name__(self, owner, name):
        pass

for _n in (
    "Char", "Integer", "Float", "Boolean", "Text", "Html", "Binary",
    "Image", "Monetary", "Selection", "Many2one", "One2many", "Many2many",
    "Json",
):
    setattr(_fields, _n, type(_n, (_FieldDescriptor,), {}))

class _MockDate(_FieldDescriptor):
    @staticmethod
    def context_today(rec=None):
        from datetime import date as _d
        return _d.today()

    @staticmethod
    def today():
        from datetime import date as _d
        return _d.today()

    @staticmethod
    def to_date(value):
        from datetime import date as _d, datetime as _dt
        if isinstance(value, _d):
            return value
        if isinstance(value, str):
            return _dt.strptime(value[:10], "%Y-%m-%d").date()
        return value

    @staticmethod
    def to_string(value):
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d")
        return str(value)


class _MockDatetime(_FieldDescriptor):
    @staticmethod
    def now():
        from datetime import datetime as _dt
        return _dt.now()

    @staticmethod
    def to_datetime(value):
        from datetime import datetime as _dt
        if isinstance(value, _dt):
            return value
        if isinstance(value, str):
            try:
                return _dt.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return _dt.strptime(value[:19], "%Y-%m-%d %H:%M:%S")
        return value

    @staticmethod
    def to_string(value):
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return str(value)


_fields.Date = _MockDate
_fields.Datetime = _MockDatetime
_odoo.fields = _fields

# odoo.models
_models = ModuleType("odoo.models")

class _ModelBase:
    pass

class _Constraint:
    def __init__(self, expr, msg=""):
        self.expr, self.msg = expr, msg

_models.Model = _ModelBase
_models.AbstractModel = _ModelBase
_models.TransientModel = _ModelBase
_models.Constraint = _Constraint
_odoo.models = _models

# odoo.exceptions
_exc = ModuleType("odoo.exceptions")

class ValidationError(Exception):
    pass

class UserError(Exception):
    pass

class AccessError(Exception):
    pass

_exc.ValidationError = ValidationError
_exc.UserError = UserError
_exc.AccessError = AccessError
_odoo.exceptions = _exc

# odoo.http (used by controllers — stub only)
_http = ModuleType("odoo.http")
_http.Controller = type("Controller", (), {})
_http.route = _deco_factory
_http.request = None
_http.Response = None
_http.content_disposition = lambda *a, **kw: ""
_odoo.http = _http

# odoo.tools
_tools = ModuleType("odoo.tools")
_tools.config = {}
_tools.float_round = lambda val, **kw: round(val, kw.get("precision_digits", 2))
_odoo.tools = _tools

# odoo.tests.common
_tests = ModuleType("odoo.tests")
_tests_common = ModuleType("odoo.tests.common")
import unittest as _ut

_tests_common.TransactionCase = _ut.TestCase
_tests_common.HttpCase = _ut.TestCase
_tests.common = _tests_common
_odoo.tests = _tests

# Register mock modules
for _path, _mod in [
    ("odoo", _odoo),
    ("odoo.api", _api),
    ("odoo.fields", _fields),
    ("odoo.models", _models),
    ("odoo.exceptions", _exc),
    ("odoo.http", _http),
    ("odoo.tools", _tools),
    ("odoo.tests", _tests),
    ("odoo.tests.common", _tests_common),
]:
    sys.modules[_path] = _mod

# ── 2. odoo.addons.* import hook ────────────────────────────────────

_addons = ModuleType("odoo.addons")
_addons.__path__ = [ADDONS_PATH]
_addons.__package__ = "odoo.addons"
_odoo.addons = _addons
sys.modules["odoo.addons"] = _addons


class _AddonFinder(importlib.abc.MetaPathFinder):
    """Maps ``odoo.addons.X.Y`` → ``custom_addons/X/Y``."""

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith("odoo.addons."):
            return None
        rel = fullname[len("odoo.addons."):]
        parts = rel.split(".")
        candidate = os.path.join(ADDONS_PATH, *parts)

        if os.path.isdir(candidate):
            init = os.path.join(candidate, "__init__.py")
            if os.path.exists(init):
                return importlib.util.spec_from_file_location(
                    fullname, init, submodule_search_locations=[candidate],
                )
        elif os.path.isfile(candidate + ".py"):
            return importlib.util.spec_from_file_location(fullname, candidate + ".py")
        return None


sys.meta_path.insert(0, _AddonFinder())

# ── 3. Add custom_addons to sys.path ────────────────────────────────

if ADDONS_PATH not in sys.path:
    sys.path.insert(0, ADDONS_PATH)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
