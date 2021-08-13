
from collections.abc import MutableMapping

from redditwarp.http.util.lingering_items_mapping import LingeringItemsMapping


def test_init() -> None:
    assert issubclass(LingeringItemsMapping, MutableMapping)

    m: LingeringItemsMapping[str, int] = LingeringItemsMapping()
    assert dict(m) == {}

    d = {'a': 1}
    m = LingeringItemsMapping(d)
    d['b'] = 2
    assert dict(m) == {'a': 1, 'b': 2}

    m = LingeringItemsMapping({'a': 1})
    assert dict(m) == {'a': 1}

    m = LingeringItemsMapping({'a': 1}, lingering_item_keys={'a'})
    assert dict(m) == {'a': 1}
    assert m.lingering_item_keys == {'a'}

def test_setitem() -> None:
    m = LingeringItemsMapping({'a': 1, 'b': 2, 'c': 3}, {'b'})
    m['a'] = 10
    m['b'] = 20
    m['c'] = 30
    assert dict(m) == {'a': 10, 'b': 2, 'c': 30}
    m.lingering_item_keys.remove('b')
    m['b'] = 20
    assert dict(m) == {'a': 10, 'b': 20, 'c': 30}

    m = LingeringItemsMapping(lingering_item_keys={'a'})
    m['a'] = 1
    assert dict(m) == {}

def test_delitem() -> None:
    m = LingeringItemsMapping({'a': 1, 'b': 2, 'c': 3}, {'b'})
    del m['a']
    del m['b']
    del m['c']
    assert dict(m) == {'b': 2}
