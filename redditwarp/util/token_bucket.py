"""An implementation of the token bucket algorithm."""

from typing import Callable

import time

class TokenBucket:
    def __init__(self, capacity: float, rate: float, *,
            time_func: Callable[[], float] = time.monotonic) -> None:
        self.capacity: float = capacity
        self.rate: float = rate
        self.time_func: Callable[[], float] = time_func
        self._value = capacity
        self._timestamp = time_func()

    def _checkpoint(self) -> float:
        now = self.time_func()
        delta = now - self._timestamp
        self._timestamp = now
        return delta

    def _replenish(self) -> None:
        if self._value < self.capacity:
            accession = self.rate * self._checkpoint()
            self._value = min(self.capacity, self._value + accession)

    def get_value(self) -> float:
        """Return the number of tokens in the bucket."""
        self._replenish()
        return self._value

    def can_consume(self, n: float) -> bool:
        """Check if `n` tokens are available."""
        return n <= self.get_value()

    def try_consume(self, n: float) -> bool:
        """Consume `n` tokens if `n` tokens are available."""
        if self.can_consume(n):
            self._value -= n
            return True
        return False

    def consume(self, n: float) -> None:
        """Consume `n` tokens. If `n` tokens aren't available, raise an exception."""
        if self.try_consume(n):
            return
        raise RuntimeError(f'attempted to consume {n} tokens when {self._value} were available')

    def hard_consume(self, n: float) -> bool:
        """Consume up to `n` tokens."""
        u = self.get_value()
        self._value = max(0, u - n)
        return n <= u

    def consume_all(self) -> None:
        """Empty the token bucket completely."""
        self._checkpoint()
        self._value = 0

    def get_cooldown(self, n: float) -> float:
        """Return the duration the client should wait before the consume
        methods return `True` again.
        """
        return max(0, (n - self.get_value()) / self.rate)
