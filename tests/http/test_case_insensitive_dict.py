
from collections.abc import MutableMapping
import pickle

import pytest

from redditwarp.http.util.case_insensitive_dict import CaseInsensitiveDict


def test_init() -> None:
    assert issubclass(CaseInsensitiveDict, MutableMapping)

    # Check that a mutable default argument isn't used.
    d1: CaseInsensitiveDict[int] = CaseInsensitiveDict()
    d2: CaseInsensitiveDict[int] = CaseInsensitiveDict()
    d1['a'] = 10
    assert 'a' in d1
    assert 'a' not in d2

    # Check that the mapping's reference is not stored.
    mydict = {'key': 1}
    d = CaseInsensitiveDict(mydict)
    mydict.clear()
    assert len(d) == 1

    mydict = {'a': 1, 'b': 2}
    assert CaseInsensitiveDict({'a': 1, 'b': 2}) == mydict
    assert mydict == CaseInsensitiveDict({'a': 1, 'b': 2})
    assert mydict == CaseInsensitiveDict({'a': 1}, b=2)
    assert mydict == CaseInsensitiveDict(a=1, b=2)

def test_contains() -> None:
    d: CaseInsensitiveDict[int] = CaseInsensitiveDict({'abc': 1})
    assert 'abc' in d
    assert 'ABC' in d
    assert 'aBC' in d

def test_iter() -> None:
    d: CaseInsensitiveDict[int] = CaseInsensitiveDict({'a': 1, 'B': 2, 'c': 3})
    assert list(d) == ['a', 'B', 'c']

def test_eq() -> None:
    CI = CaseInsensitiveDict
    assert CI({'e': 1}) == {'e': 1}
    assert {'e': 1} == CI({'e': 1})
    assert CI({'e': 1}) == CI({'E': 1})
    assert CI({'E': 1}) == CI({'e': 1})
    assert CI({'e': 1}) == {'E': 1}
    assert {'E': 1} == CI({'e': 1})

    assert CI({'e': 1}) != {'f': 1}

def test_getitem() -> None:
    d = CaseInsensitiveDict({'b': {'bb': 22}})
    # Not recursive
    assert type(d['b']) is dict
    assert d['b']['bb'] == 22

    d2 = CaseInsensitiveDict({'abc': 1})
    assert d2['abc'] == d2['ABC'] == d2['AbC'] == d2['aBC'] == 1

    with pytest.raises(KeyError):
        d2['z']

def test_setitem() -> None:
    d: CaseInsensitiveDict[int] = CaseInsensitiveDict({'a': 1})
    assert len(d) == 1
    d['b'] = 2
    assert d['b'] == d['B'] == 2
    assert len(d) == 2

    assert list(d) == ['a', 'b']
    d['A'] = 1
    assert list(d) == ['A', 'b']

def test_delitem() -> None:
    d: CaseInsensitiveDict[int] = CaseInsensitiveDict({'a': 1, 'b': 2, 'c': 3})
    assert len(d) == 3

    del d['c']
    assert 'c' not in d
    assert len(d) == 2

    del d['B']
    assert 'B' not in d
    assert len(d) == 1

def test_update() -> None:
    d: CaseInsensitiveDict[int] = CaseInsensitiveDict({'a': 1, 'b': 2, 'c': 3})
    assert len(d) == 3
    d.update({'C': 8, 'D': 11})
    assert len(d) == 4
    assert d['a'] == 1
    assert d['b'] == 2
    assert d['c'] == 8
    assert d['d'] == 11

def test_clear() -> None:
    d: CaseInsensitiveDict[int] = CaseInsensitiveDict({'a': 1, 'b': 2, 'c': 3})
    assert len(d) == 3
    d.clear()
    assert len(d) == 0

def test_pickle() -> None:
    mydict = {
        'a': 1,
        'b': 2,
        'c': {'dee': 40, 'eee': {'eff': 'gee', 'hch': 80}},
        'foo': [1, 2, 3],
    }
    d: object = CaseInsensitiveDict(mydict)
    for level in range(pickle.HIGHEST_PROTOCOL + 1):
        other = pickle.loads(pickle.dumps(d, protocol=level))
        assert d == other
