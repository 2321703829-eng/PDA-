"""测试辅助工具 — MockRecord / MockRecordset / MockEnv。"""

from unittest.mock import MagicMock


class MockRecord:
    """模拟单条 Odoo 记录。"""

    def __init__(self, _id=1, **fields):
        self.id = _id
        for k, v in fields.items():
            setattr(self, k, v)

    def __bool__(self):
        return True

    def __eq__(self, other):
        if isinstance(other, MockRecord):
            return self.id == other.id
        if isinstance(other, _EmptyRecord):
            return False
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self):
        return hash(self.id)

    def __getitem__(self, key):
        return getattr(self, key)

    def write(self, vals):
        for k, v in vals.items():
            setattr(self, k, v)


class _EmptyRecord:
    """模拟空记录 / False-like record。"""
    id = False

    def __bool__(self):
        return False

    def __getattr__(self, name):
        return False

    def __eq__(self, other):
        if isinstance(other, _EmptyRecord):
            return True
        if isinstance(other, MockRecord):
            return False
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self):
        return hash(False)


EMPTY = _EmptyRecord()


class MockRecordset:
    """模拟 Odoo 记录集。"""

    def __init__(self, records=None, env=None):
        self._records = list(records or [])
        self.env = env or MagicMock()

    def __iter__(self):
        return iter(self._records)

    def __len__(self):
        return len(self._records)

    def __bool__(self):
        return len(self._records) > 0

    def __getitem__(self, key):
        if isinstance(key, slice):
            return MockRecordset(self._records[key], self.env)
        return self._records[key]

    def __or__(self, other):
        seen = set()
        merged = []
        for r in self._records + list(other):
            if id(r) not in seen:
                seen.add(id(r))
                merged.append(r)
        return MockRecordset(merged, self.env)

    def __getattr__(self, name):
        if name.startswith("_") or name in ("env",):
            raise AttributeError(name)
        if len(self._records) == 1:
            return getattr(self._records[0], name)
        raise AttributeError("Cannot access field %r on multi-record set" % name)

    def ensure_one(self):
        assert len(self._records) == 1, "Expected 1 record, got %d" % len(self._records)
        return self

    @property
    def ids(self):
        return [r.id for r in self._records]

    def mapped(self, field):
        result = []
        for r in self._records:
            val = getattr(r, field, None)
            if val is not None:
                result.append(val)
        return result

    def filtered(self, func):
        return MockRecordset([r for r in self._records if func(r)], self.env)

    def sorted(self, key=None, reverse=False):
        return MockRecordset(sorted(self._records, key=key, reverse=reverse), self.env)

    def search(self, domain, limit=None):
        return MockRecordset([], self.env)

    def browse(self, ids):
        return MockRecordset([], self.env)

    def sudo(self):
        return self

    def write(self, vals):
        for r in self._records:
            for k, v in vals.items():
                setattr(r, k, v)

    def invalidate_recordset(self):
        pass
