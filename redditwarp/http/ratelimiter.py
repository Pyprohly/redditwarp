
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
		self._replenish()
		return self._value

	def consume(self, n: float) -> bool:
		"""Comsume `n` tokens if `n` tokens are available."""
		self._replenish()
		if self._value >= n:
			self._value -= n
			return True
		return False

	def hard_consume(self, n: float) -> bool:
		"""Comsume up to `n` tokens."""
		self._replenish()
		old_value = self._value

		self._value -= n
		if self._value < 0:
			self._value = 0

		return old_value >= n

	def cooldown(self, n: float) -> float:
		"""Return the duration the client should wait before `self.comsume()`
		becomes `True` again.

			async with lock:
				if not tb.consume(1):
					await asyncio.sleep(tb.cooldown(1))
					tb.consume(1)
		"""
		return max(0, (n - self._value)/self.rate)


from .ratelimiter_sync import RateLimited as RateLimitedSync, RateLimited
from .ratelimiter_async import RateLimited as RateLimitedAsync
