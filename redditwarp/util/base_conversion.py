
from typing import Sequence, List

def base_digits(base: int, n: int) -> Sequence[int]:
    if base < 2:
        raise ValueError('`base` must be at least 2')
    if n < 0:
        raise ValueError('`n` must be positive')

    digits: List[int] = []
    digits_append = digits.append
    while n:
        digits_append(n % base)
        n //= base
    return digits

def to_base(base: int, n: int, alphabet: str) -> str:
    if base > len(alphabet):
        raise ValueError('alphabet not large enough')

    sign = '-' if n < 0 else ''
    n = abs(n)
    digits = base_digits(base, n)
    return sign + ''.join(reversed([alphabet[i] for i in digits]))

def to_base36(n: int) -> str:
    return to_base(36, n, '0123456789abcdefghijklmnopqrstuvwxyz')
