
import os

import pytest  # type: ignore[import]

from redditwarp.util.data_members_namespace import DataMembersNamespace, DataMembersMapping

class A:
    def __init__(self) -> None:
        self.aaa = 1

    @property
    def bbb(self) -> int:
        return 2

    def ccc(self) -> int:
        return 3

class B(A):
    pass

class C(B):
    def __init__(self) -> None:
        super().__init__()
        self.ddd = 4
        self.eee = lambda: 5


class TestDataAttributeNamespace:
    def test_getattr(self) -> None:
        d = DataMembersNamespace(C())
        assert d.aaa == 1
        assert d.bbb == 2
        assert d.ddd == 4
        assert d.eee() == 5

        with pytest.raises(AttributeError):
            d.ccc

        with pytest.raises(AttributeError):
            d.zzz

    def test_iter(self) -> None:
        assert list(DataMembersNamespace(C())) == ['aaa', 'bbb', 'ddd', 'eee']

    def test_len(self) -> None:
        assert len(DataMembersNamespace(C())) == 4

    def test_contains(self) -> None:
        d = DataMembersNamespace(C())
        assert 'aaa' in d
        assert 'bbb' in d
        assert 'ccc' not in d
        assert 'ddd' in d
        assert 'eee' in d

    def test_dir(self) -> None:
        d = DataMembersNamespace(C())
        assert dir(d) == ['aaa', 'bbb', 'ddd', 'eee']

    def test_print(self) -> None:
        # Check no exception raised
        with open(os.devnull, 'w') as null:
            print(DataMembersNamespace(C()), file=null)

class TestDataMembersMapping:
    def test_general(self) -> None:
        assert issubclass(DataMembersMapping, DataMembersNamespace)

    def test_getitem(self) -> None:
        d = DataMembersMapping(C())
        assert d['aaa'] == 1
        assert d['bbb'] == 2
        assert d['ddd'] == 4
        assert d['eee']() == 5

        with pytest.raises(KeyError):
            d['ccc']
        with pytest.raises(KeyError):
            d['zzz']
