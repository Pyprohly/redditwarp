
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .requestor import Requestor
	from .request import Request
	from .response import Response

from time import sleep

from .requestor import RequestorDecorator

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

		sleep(s)

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


from .ratelimiter import TokenBucket
