
from __future__ import annotations
from collections.abc import Iterable

def base_digits(base: int, n: int) -> Iterable[int]:
    if base < 2:
        raise ValueError('`base` must be at least 2')
    if n < 0:
        raise ValueError('`n` must be positive')

    def g(base: int, n: int) -> Iterable[int]:
        while n:
            n, r = divmod(n, base)
            yield r

    return g(base, n)

def to_base(base: int, n: int, alphabet: str = "0123456789abcdefghijklmnopqrstuvwxyz") -> str:
    if base > len(alphabet):
        raise ValueError('alphabet is not large enough')
    if n == 0:
        return alphabet[0]
    sign = '-' if n < 0 else ''
    numbers = base_digits(base, abs(n))
    symbols = (alphabet[i] for i in numbers)
    return sign + ''.join(reversed(list(symbols)))

def to_base36(n: int, alphabet: str = "0123456789abcdefghijklmnopqrstuvwxyz") -> str:
    return to_base(36, n, alphabet=alphabet)
