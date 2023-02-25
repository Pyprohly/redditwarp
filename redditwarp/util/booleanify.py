
from __future__ import annotations
from typing import Mapping

_TRUTHY_WORDS = {'1', 'true', 't', 'on', 'yes', 'y'}
_FALSY_WORDS = {'0', 'false', 'f', 'off', 'no', 'n'}

_BOOLEAN_WORDS: Mapping[str, bool] = {
    **{x: True for x in _TRUTHY_WORDS},
    **{x: False for x in _FALSY_WORDS},
}

def booleanify(s: str) -> bool:
    """Convert a string to boolean.

    An empty string is `False`.

    Raises `ValueError` if the given string is not booleanifiable.

    Booleanifiable strings:

    - Truthy: `{'1', 'true', 't', 'on', 'yes', 'y'}`
    - Falsy: `{'0', 'false', 'f', 'off', 'no', 'n'}`
    """
    if s == '':
        return False
    try:
        return _BOOLEAN_WORDS[s.lower()]
    except KeyError:
        pass
    raise ValueError('Not booleanifiable: %r' % s)
