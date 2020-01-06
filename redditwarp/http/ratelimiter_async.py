
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .requestor import Requestor
	from .request import Request
	from .response import Response

import asyncio
import time
from asyncio import sleep

from .requestor import RequestorDecorator

class RateLimited(RequestorDecorator):
	def __init__(self, requestor: Requestor) -> None:
		super().__init__(requestor)
		self.token_bucket = TokenBucket(10, 1.1)
		self.reset = 0
		self.remaining = 0
		self.used = 0
		self._previous_request = 0
		self._last_request = time.monotonic()
		self._lock = asyncio.Lock()

	async def request(self, request: Request, timeout: Optional[int]) -> Response:
		s = 0
		if self.remaining:
			s = self.reset / self.remaining

		async with self._lock:
			if s > 1:
				await sleep(s)
				self.token_bucket.hard_consume(s)

			if not self.token_bucket.consume(1):
				c = self.token_bucket.cooldown(1)
				await sleep(c)
				self.token_bucket.consume(1)

		self._previous_request = self._last_request
		self._last_request = time.monotonic()

		response = await self.requestor.request(request, timeout)

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
			self.reset -= int(self._last_request - self._previous_request)
			self.remaining -= 1
			self.used += 1


from .ratelimiter import TokenBucket
