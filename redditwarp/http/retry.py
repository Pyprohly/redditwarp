
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .requestor import Requestor
	from .request import Request
	from .response import Response

import time

from .requestor import RequestorDecorator
from .exceptions import HTTPResponseError, http_error_response_classes

class Retryable(RequestorDecorator):
	def request(self, request: Request, timeout: Optional[int]) -> Response:

		for i in range(5):
			response = self.requestor.request(request, timeout)
			status = response.status

			if 200 <= status < 300:
				return response

			if status == 429:
				assert False
				raise AssertionError('429 response')

			if status in (500, 502):
				time.sleep(2*i + 1)
				continue

			break


		try:
			clss = http_error_response_classes(response)
		except KeyError:
			clss = HTTPResponseError

		raise clss(response)
