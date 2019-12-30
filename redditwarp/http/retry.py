
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .requestor import Requestor
	from .request import Request
	from .response import Response

from .requestor import RequestorDecorator

class RateLimited(RequestorDecorator):
	def request(self, request: Request, timeout: Optional[int]) -> Response:

		for t in range(5):
			response = self.requestor.request(request, timeout)
			status = response.status

			if 200 <= status < 300:
				break

			if status == 429:
				assert False
				raise AssertionError('429 response')

			if status in (500, 502):
				continue

			raise HTTPResponseErrorFactory(response)

		return response
