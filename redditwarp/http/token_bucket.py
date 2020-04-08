
from typing import Callable
import time

class TokenBucket:
	def __init__(self, capacity: float, rate: float,
			time_func: Callable[[], float] = time.monotonic) -> None:
		self.capacity = capacity
		self.rate = rate
		self.time_func = time_func
		self._value = capacity
		self._last_update = time_func()

	def _checkpoint_time(self) -> float:
		now = self.time_func()
		time_delta = now - self._last_update
		self._last_update = now
		return time_delta

	def _replenish(self) -> None:
		if self._value < self.capacity:
			new_tokens = self.rate * self._checkpoint_time()
			self._value = min(self._value + new_tokens, self.capacity)

	def get_value(self) -> float:
		"""Return the number of tokens in the bucket."""
		self._replenish()
		return self._value

	def can_consume(self, n: float) -> bool:
		"""Check if `n` tokens are available."""
		return n <= self.get_value()

	def try_consume(self, n: float) -> bool:
		"""Comsume `n` tokens if `n` tokens are available."""
		if self.can_consume(n):
			self._value -= n
			return True
		return False

	def do_consume(self, n: float) -> bool:
		"""Comsume `n` tokens. Raise an exception if `n` tokens aren't available."""
		if self.try_consume(n):
			return True
		raise RuntimeError(f'attempted consume of {n} token(s) when {self._value} were available')

	def hard_consume(self, n: float) -> bool:
		"""Comsume up to `n` tokens."""
		t = self.get_value()
		self._value = max(self._value - n, 0)
		return n <= t

	def consume_all(self) -> None:
		"""Deplete the token bucket. Like `self.hard_consume(float('inf'))`."""
		self._checkpoint_time()
		self._value = 0

	def cooldown(self, n: float) -> float:
		"""Return the duration the client should wait before the `*_comsume`
		methods return `True` again.

		This class is not IO-bound so there is no "`wait_consume()`" method.
		Here is the logic for that::

			t = 2
			async with lock:
				if not tb.try_consume(t):
					await asyncio.sleep(tb.cooldown(t))
					tb.do_consume(t)
		"""
		return max(0, (n - self._value)/self.rate)
