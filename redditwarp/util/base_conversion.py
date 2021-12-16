
from __future__ import annotations

def base_digits(base: int, n: int) -> list[int]:
    if base < 2:
        raise ValueError('`base` must be at least 2')
    if n < 0:
        raise ValueError('`n` must be positive')

    digits = []
    while n:
        n, r = divmod(n, base)
        digits.append(r)
    return digits

def to_base(base: int, n: int, alphabet: str) -> str:
    if base > len(alphabet):
        raise ValueError('alphabet not large enough')
    if n == 0:
        return alphabet[0]

    sign = '-' if n < 0 else ''
    digits = base_digits(base, abs(n))
    return sign + ''.join(reversed([alphabet[x] for x in digits]))

def to_base36(n: int) -> str:
    return to_base(36, n, '0123456789abcdefghijklmnopqrstuvwxyz')
