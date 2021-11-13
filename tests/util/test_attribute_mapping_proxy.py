
from typing import Any

import pickle

import pytest

from redditwarp.util.attribute_mapping_proxy import (
    AttributeMappingProxy,
    MappingRecursiveAttributeMappingProxy,
    MappingAndSequenceRecursiveAttributeMappingProxy,
)


class Test_AttributeMappingProxy:
    def test_getitem(self) -> None:
        d: dict[str, object] = {'a': 1, 'b': {'aa': 3}}
        amp = AttributeMappingProxy(d)
        assert amp['a'] == 1
        d_b = amp['b']
        assert type(d_b) is dict
        assert d_b['aa'] == 3

        with pytest.raises(KeyError):
            amp['z']

    def test_getattr(self) -> None:
        d = {'a': 1, 'b': {'bb': 22}}
        amp = AttributeMappingProxy(d)
        assert amp.a == 1
        assert type(amp.b) is dict
        assert amp.b == {'bb': 22}

        with pytest.raises(AttributeError):
            amp.z

    def test_iter(self) -> None:
        assert set(AttributeMappingProxy({'a': 1, 'b': 2, 'c': 3})) == {'a', 'b', 'c'}

    def test_dir(self) -> None:
        d = {'a': 1, 'b': 2, 'c': 3}
        amp = AttributeMappingProxy(d)
        assert dir(amp) == sorted(amp)

    def test_abs(self) -> None:
        d: dict[str, int] = {}
        amp = AttributeMappingProxy(d)
        assert abs(amp) is d

    def test_pickle(self) -> None:
        mydict = {
            'a': 1,
            'b': 2,
            'c': {'dee': 40, 'eee': {'eff': 'gee', 'aych': 80}},
            'foo': [1, 2, 3],
        }
        amp = AttributeMappingProxy(mydict)
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(amp, protocol=level))
            assert amp == other


class Test_MappingRecursiveAttributeMappingProxy:
    def test_getattr(self) -> None:
        d = {'a': 1, 'b': {'bb': 22}, 'c': {'cc': {'ccc': 333}}}
        amp = MappingRecursiveAttributeMappingProxy(d)
        assert amp.a == 1
        assert amp.b == MappingRecursiveAttributeMappingProxy({'bb': 22})
        assert amp.b.bb == 22
        assert amp.c.cc.ccc == 333


class Test_MappingAndSequenceRecursiveAttributeMappingProxy:
    def test_getattr(self) -> None:
        d: dict[str, Any] = {'a': {'aa': [{'b': 1}, {'b': 2}]}}
        amp = MappingAndSequenceRecursiveAttributeMappingProxy(d)
        assert amp.a.aa[0].b == 1
        assert amp.a.aa[1].b == 2

        d = {'a': [None, [{'b': {'c': [{'d': 2}]}}]]}
        amp = MappingAndSequenceRecursiveAttributeMappingProxy(d)
        assert amp.a[1][0].b.c[0].d == 2
