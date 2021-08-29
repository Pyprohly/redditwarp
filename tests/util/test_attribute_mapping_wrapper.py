
from typing import Dict, Any, cast

from collections.abc import MutableMapping
import pickle

import pytest

from redditwarp.util.attribute_mapping_wrapper import MutableAttributeMappingWrapper


def test_subclass() -> None:
    assert issubclass(MutableAttributeMappingWrapper, MutableMapping)

def test_constructor() -> None:
    d: Dict[str, int] = {}
    amw = MutableAttributeMappingWrapper(d)
    assert abs(amw) is d

def test_getitem() -> None:
    d = {'a': 1, 'b': {'aa': 3}}
    amw = MutableAttributeMappingWrapper(d)
    assert amw['a'] == 1
    assert type(amw['b']) is dict
    assert cast(Dict[str, int], amw['b'])['aa'] == 3

    with pytest.raises(KeyError):
        amw['z']

def test_setitem() -> None:
    d: Dict[str, object] = {'a': 1, 'b': 2}
    amw = MutableAttributeMappingWrapper(d)
    assert len(amw) == 2

    amw['c'] = 4
    assert amw['c'] == 4
    assert len(amw) == 3

    amw['d'] = {'dd': 4}
    assert type(amw['d']) is dict
    assert cast(Dict[str, int], amw['d'])['dd'] == 4

def test_delitem() -> None:
    d = {'a': 1, 'b': 2, 'c': 3}
    amw = MutableAttributeMappingWrapper(d)
    assert len(amw) == 3
    del amw['c']
    assert 'c' not in amw
    assert len(amw) == 2

def test_getattr() -> None:
    d = {'a': 1, 'b': {'bb': 22}}
    amw = MutableAttributeMappingWrapper(d)
    assert amw.a == 1

    assert type(amw.b) is MutableAttributeMappingWrapper
    assert dict(amw.b) == {'bb': 22}
    assert amw.b.bb == 22

    with pytest.raises(AttributeError):
        amw.z
    with pytest.raises(AttributeError):
        cast(MutableAttributeMappingWrapper[int], amw['b']).bb

def test_setattr() -> None:
    d: Dict[str, Any] = {'a': 1, 'b': 2}
    amw = MutableAttributeMappingWrapper(d)
    assert len(amw) == 2
    amw.d = 4
    assert amw['d'] == 4
    assert len(amw) == 3

    amw.c = {'cc': 33}
    assert type(amw['c']) is dict
    assert type(amw.c).__name__ == MutableAttributeMappingWrapper.__name__

def test_delattr() -> None:
    d = {'a': 1, 'b': 2, 'c': 3}
    amw = MutableAttributeMappingWrapper(d)
    assert len(amw) == 3
    del amw.c  # type: ignore
    assert 'c' not in amw
    assert len(amw) == 2

def test_iter() -> None:
    assert set(MutableAttributeMappingWrapper({'a': 1, 'b': 2, 'c': 3})) == {'a', 'b', 'c'}

def test_dir() -> None:
    d = {'a': 1, 'b': 2, 'c': 3}
    amw = MutableAttributeMappingWrapper(d)
    assert dir(amw) == sorted(amw)

def test_abs() -> None:
    d = {'key': 'value'}
    amw = MutableAttributeMappingWrapper(d)
    d['key2'] = 'value2'
    assert 'key2' in amw
    assert amw['key2'] == 'value2'
    assert abs(amw) is d

def test_update() -> None:
    d = {'a': 1, 'b': 2, 'c': 3}
    amw = MutableAttributeMappingWrapper(d)
    assert len(amw) == 3
    amw.update({'c': 8, 'd': 11})
    assert len(amw) == 4
    assert amw['a'] == 1
    assert amw['b'] == 2
    assert amw['c'] == 8
    assert amw['d'] == 11

def test_clear() -> None:
    d = {'a': 1, 'b': 2, 'c': 3}
    amw = MutableAttributeMappingWrapper(d)
    assert len(amw) == 3
    amw.clear()
    assert len(amw) == 0
    assert abs(amw) is d

def test_pickle() -> None:
    mydict = {
        'a': 1,
        'b': 2,
        'c': {'dee': 40, 'eee': {'eff': 'gee', 'aych': 80}},
        'foo': [1, 2, 3],
    }
    amw = MutableAttributeMappingWrapper(mydict)
    for level in range(pickle.HIGHEST_PROTOCOL + 1):
        other = pickle.loads(pickle.dumps(amw, protocol=level))
        assert amw == other

def test_noclobber_mapping_methods() -> None:
    d: Dict[str, int] = {}
    amw = MutableAttributeMappingWrapper(d)
    update_method = amw.update
    clear_method = amw.clear

    amw.update = 1  # type: ignore[assignment]
    assert amw['update'] == 1
    assert amw.update == update_method

    amw.update({'clear': 2})  # type: ignore
    assert amw['clear'] == 2
    assert amw.clear == clear_method  # type: ignore
