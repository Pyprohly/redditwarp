
import time

class TokenBucket:
	def __init__(self, capacity: float, rate: float) -> None:
		self.capacity = capacity
		self.rate = rate
		self.last_update = time.time()
		self._value = capacity

	def _replenish(self) -> None:
		if self._value < self.capacity:
			now = time.time()
			time_delta = now - self.last_update
			self._value = min(self.capacity, self._value + self.rate * time_delta)
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
		"""
		return max(0, (n - self.get_value())/self.rate)


from .ratelimiter_sync import RateLimited as RateLimitedSync, RateLimited
from .ratelimiter_async import RateLimited as RateLimitedAsync
