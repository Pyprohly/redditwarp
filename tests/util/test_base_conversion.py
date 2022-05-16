
import pytest

from redditwarp.util.base_conversion import base_digits, to_base, to_base36

def test_base_digits() -> None:
    assert list(base_digits(10, 1746)) == [6,4,7,1]
    assert ''.join(map(str, reversed(list(base_digits(10, 385))))) == '385'
    assert list(base_digits(36, 1746)) == [18, 12, 1]
    assert list(base_digits(17, 0)) == []

    with pytest.raises(ValueError):
        base_digits(1, 99)
    with pytest.raises(ValueError):
        base_digits(99, -1)

def test_to_base() -> None:
    assert to_base(4, 643, '0123') == '22003'
    assert to_base(8, -234, '01234567') == '-352'

    with pytest.raises(ValueError):
        assert to_base(1, 99, '1')

    to_base(20, -1, '1'*50)
    with pytest.raises(ValueError):
        assert to_base(50, -1, '1'*20)

    assert to_base(5, 0, '01234') == '0'
    assert to_base(5, 0, '43210') == '4'

def test_to_base36() -> None:
    assert to_base36(int('f6jnzr', 36)) == 'f6jnzr'
    assert to_base36(-int('a05z1', 36)) == '-a05z1'
