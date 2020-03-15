
from typing import Callable
import time

class TokenBucket:
	def __init__(self, capacity: float, rate: float,
			time_func: Callable[[], float] = time.monotonic) -> None:
		self.capacity = capacity
		self.rate = rate
		self.time_func = time_func
		self.last_update = time_func()
		self._value = capacity

	def _replenish(self) -> None:
		if self._value < self.capacity:
			now = self.time_func()
			time_delta = now - self.last_update
			new_tokens = self.rate * time_delta
			self._value = min(self.capacity, self._value + new_tokens)
			self.last_update = now

	def get_value(self) -> float:
		"""Return the number of tokens in the bucket."""
		self._replenish()
		return self._value

	def can_consume(self, n: float) -> bool:
		"""Check if `n` tokens are available."""
		self._replenish()
		return self._value >= n

	def try_consume(self, n: float) -> bool:
		"""Comsume `n` tokens if `n` tokens are available."""
		self._replenish()
		if self._value >= n:
			self._value -= n
			return True
		return False

	def hard_consume(self, n: float) -> bool:
		"""Comsume up to `n` tokens, regardless if there aren't that many."""
		self._replenish()
		prev_value = self._value
		self._value = max(self._value - n, 0)
		return prev_value >= n

	def cooldown(self, n: float) -> float:
		"""Return the duration the client should wait before the `*_comsume`
		methods return `True` again.

		This class is not IO-bound so there is no "`wait_consume()`" method.
		Here is the logic for that::

			t = 1
			async with lock:
				if not tb.try_consume(t):
					await asyncio.sleep(tb.cooldown(t))
					u = tb.hard_consume(t)
					assert u
		"""
		return max(0, (n - self._value)/self.rate)


from .ratelimiter_sync import RateLimited as RateLimitedSync, RateLimited
from .ratelimiter_async import RateLimited as RateLimitedAsync
