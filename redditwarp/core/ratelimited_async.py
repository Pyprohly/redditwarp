
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from collections.abc import Mapping
	from ..http.requestor_async import Requestor
	from ..http.request import Request
	from ..http.response import Response

import asyncio
import time
from asyncio import sleep

from ..http.requestor_async import RequestorDecorator
from .token_bucket import TokenBucket

class RateLimited(RequestorDecorator):
	def __init__(self, requestor: Requestor) -> None:
		super().__init__(requestor)
		self.reset = 0.
		self.remaining = 0.
		self.used = 0.
		self._rate_limiting_tb = TokenBucket(10, 1.1)
		self._prev_request = 0.
		self._last_request = time.monotonic()
		self._lock = asyncio.Lock()

	async def request(self, request: Request, *, timeout: Optional[float] = None,
			auxiliary: Optional[Mapping] = None) -> Response:
		s = 0.
		if self.remaining:
			# Note: in async code we can't rely on the value of this result
			# being current because of the possibility of concurrency.
			s = self.reset / self.remaining

		tb = self._rate_limiting_tb
		async with self._lock:
			# If the API wants us to sleep for longer than a second, obey.
			if s > 1:
				await sleep(s)

				# Don't add any tokens for the time spent sleeping here,
				# so the rate limiting is the conjunction of what the API
				# wants and what the token bucket wants.
				tb.do_consume(s)

			if not tb.try_consume(1):
				await sleep(tb.cooldown(1))
				tb.do_consume(1)

		self._prev_request = self._last_request
		self._last_request = time.monotonic()

		response = await self.requestor.request(request, timeout=timeout, auxiliary=auxiliary)

		self.scan_ratelimit_headers(response.headers)
		return response

	def scan_ratelimit_headers(self, headers: Mapping[str, str]) -> None:
		if 'x-ratelimit-reset' in headers:
			self.reset = float(headers['x-ratelimit-reset'])
			self.remaining = float(headers['x-ratelimit-remaining'])
			self.used = float(headers['x-ratelimit-used'])
			return

		if self.reset > 0:
			self.reset -= int(self._last_request - self._prev_request)
			self.remaining -= 1
			self.used += 1
		else:
			self.reset = 100
			self.remaining = 200
			self.used = 0
