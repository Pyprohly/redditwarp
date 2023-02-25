"""Convert integers to strings representing numbers of various bases."""

from __future__ import annotations
from collections.abc import Iterable

def base_digits(base: int, n: int) -> Iterable[int]:
    """Yield the base digits of number `n`.

    A `ValueError` is raised if `base < 2` or `n <= 0`.

    ::

       >>> list(base_digits(10, 123))
       [3, 2, 1]
       >>> list(base_digits(16, 123))
       [11, 7]
       >>> list(base_digits(8, 123))
       [3, 7, 1]
       >>> list(base_digits(2, 123))
       [1, 1, 0, 1, 1, 1, 1]
    """
    if base < 2:
        raise ValueError("`base` must be at least 2")
    if n <= 0:
        raise ValueError("`n` must be positive")

    def g(base: int, n: int) -> Iterable[int]:
        while n:
            n, r = divmod(n, base)
            yield r

    return g(base, n)

def to_base(base: int, n: int, alphabet: str = "0123456789abcdefghijklmnopqrstuvwxyz") -> str:
    """Convert number `n` to base `base`."""
    if base > len(alphabet):
        raise ValueError("`alphabet` is not large enough for the given `base`")
    if n == 0:
        return alphabet[0]
    sign = '-' if n < 0 else ''
    numbers = base_digits(base, abs(n))
    symbols = [alphabet[i] for i in numbers]
    return sign + ''.join(reversed(symbols))

def to_base36(n: int, alphabet: str = "0123456789abcdefghijklmnopqrstuvwxyz") -> str:
    """Convert number `n` to base 36."""
    return to_base(36, n, alphabet=alphabet)
