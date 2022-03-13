
from collections.abc import MutableMapping

from redditwarp.http.util.locked_keys_mapping_proxy import LockedKeysMappingProxy


def test_init() -> None:
    assert issubclass(LockedKeysMappingProxy, MutableMapping)

    d = {'a': 1}
    m = LockedKeysMappingProxy(d)
    d['b'] = 2
    assert dict(m) == {'a': 1, 'b': 2}

    m = LockedKeysMappingProxy({'a': 1})
    assert dict(m) == {'a': 1}

    m = LockedKeysMappingProxy({'a': 1}, locked_keys={'a'})
    assert dict(m) == {'a': 1}
    assert m.locked_keys == {'a'}

def test_setitem() -> None:
    m = LockedKeysMappingProxy({'a': 1, 'b': 2, 'c': 3}, {'b'})
    m['a'] = 10
    m['b'] = 20
    m['c'] = 30
    assert dict(m) == {'a': 10, 'b': 2, 'c': 30}
    m.locked_keys.remove('b')
    m['b'] = 20
    assert dict(m) == {'a': 10, 'b': 20, 'c': 30}

    m = LockedKeysMappingProxy({}, locked_keys={'a'})
    m['a'] = 1
    assert dict(m) == {}

def test_delitem() -> None:
    m = LockedKeysMappingProxy({'a': 1, 'b': 2, 'c': 3}, {'b'})
    del m['a']
    del m['b']
    del m['c']
    assert dict(m) == {'b': 2}
