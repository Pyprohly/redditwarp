
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .requestor import Requestor
	from .request import Request
	from .response import Response

import time

from .requestor import RequestorDecorator


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


class RateLimited(RequestorDecorator):
	def __init__(self, requestor: Requestor) -> None:
		super().__init__(requestor)
		self.token_bucket = TokenBucket(6, .5)
		self.reset = 0
		self.remaining = 0
		self.used = 0

	def request(self, request: Request, timeout: Optional[int]) -> Response:
		s = 0
		if self.remaining:
			s = self.reset / self.remaining

		cons = self.token_bucket.hard_consume(1)
		if cons and s < 1:
			s = 0

		time.sleep(s)

		response = self.requestor.request(request, timeout)
		self.parse_ratelimit_headers(response.headers)
		return response

	def parse_ratelimit_headers(self, headers):
		if 'x-ratelimit-reset' in headers:
			self.reset = float(headers['x-ratelimit-reset'])
			self.remaining = float(headers['x-ratelimit-remaining'])
			self.used = float(headers['x-ratelimit-used'])
			return

		if self.reset < 1:
			self.reset = 100
			self.remaining = 200
			self.used = 0
		else:
			self.reset -= 1
			self.remaining -= 1
			self.used += 1
