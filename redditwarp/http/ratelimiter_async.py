
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from collections.abc import Mapping
	from .requestor_async import Requestor
	from .request import Request
	from .response import Response

import asyncio
import time
from asyncio import sleep

from .requestor_async import RequestorDecorator

class RateLimited(RequestorDecorator):
	def __init__(self, requestor: Requestor) -> None:
		super().__init__(requestor)
		self.reset = 0.
		self.remaining = 0.
		self.used = 0.
		self._ratelimiting_tb = TokenBucket(10, 1.1)
		self._previous_request = 0.
		self._last_request = time.monotonic()
		self._lock = asyncio.Lock()

	async def request(self, request: Request, timeout: Optional[int] = None) -> Response:
		s = 0.
		if self.remaining:
			# Note: in async code we can't rely on the value of this result
			# being current because of the possibility of concurrency.
			s = self.reset / self.remaining

		tb = self._ratelimiting_tb
		async with self._lock:
			# If the API wants us to sleep for longer than a second, obey.
			if s > 1:
				await sleep(s)

				# Don't add any tokens for the time spent sleeping here,
				# so the rate limiting is the conjunction of what the API
				# wants and what the token bucket wants.
				tb.hard_consume(s)

			if not tb.try_consume(1):
				c = tb.cooldown(1)
				await sleep(c)
				tb.try_consume(1)

		self._previous_request = self._last_request
		self._last_request = time.monotonic()

		response = await self.requestor.request(request, timeout)

		self.scan_ratelimit_headers(response.headers)
		return response

	def scan_ratelimit_headers(self, headers: Mapping[str, str]):
		if 'x-ratelimit-reset' in headers:
			self.reset = float(headers['x-ratelimit-reset'])
			self.remaining = float(headers['x-ratelimit-remaining'])
			self.used = float(headers['x-ratelimit-used'])
			return

		if self.reset > 0:
			self.reset -= int(self._last_request - self._previous_request)
			self.remaining -= 1
			self.used += 1
		else:
			self.reset = 100
			self.remaining = 200
			self.used = 0


from .ratelimiter import TokenBucket
