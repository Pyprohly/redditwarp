
from typing import Callable
import time

class TokenBucket:
    def __init__(self, capacity: float, rate: float,
            time_func: Callable[[], float] = time.monotonic) -> None:
        self.capacity: float = capacity
        self.rate: float = rate
        self.time_func: Callable[[], float] = time_func
        self._value = capacity
        self._last_checkpoint_time = time_func()

    def _checkpoint_time(self) -> float:
        now = self.time_func()
        delta = now - self._last_checkpoint_time
        self._last_checkpoint_time = now
        return delta

    def _replenish(self) -> None:
        if self._value < self.capacity:
            accretion = self.rate * self._checkpoint_time()
            self._value = min(self._value + accretion, self.capacity)

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

    def do_consume(self, n: float) -> bool:
        """Consume `n` tokens. If `n` tokens aren't available, raise an exception."""
        if self.try_consume(n):
            return True
        raise RuntimeError(f'attempted to consume {n} tokens when {self._value} were available')

    def hard_consume(self, n: float) -> bool:
        """Consume up to `n` tokens."""
        u = self.get_value()
        self._value = max(u - n, 0)
        return n <= u

    def consume_all(self) -> None:
        """Empty the token bucket completely. Like `self.hard_consume(float('inf'))`."""
        self._checkpoint_time()
        self._value = 0

    def get_cooldown(self, n: float) -> float:
        """Return the duration the client should wait before the consume
        methods will return `True` again.

        There is no `wait_consume()` method on this class because it aims to not be IO-bound.
        Here is the logic for implementing such a method::

            async with lock:
                t = 1
                if not tb.try_consume(t):
                    await asyncio.sleep(tb.get_cooldown(t))
                    tb.do_consume(t)
        """
        return max((n - self.get_value()) / self.rate, 0)
