
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
if TYPE_CHECKING:
	from .requestor_sync import Requestor
	from .request import Request
	from .response import Response

from .requestor_sync import RequestorDecorator

class DefaultHeaderReceptive(RequestorDecorator):
	def __init__(self, requestor: Requestor, headers: Optional[Mapping[str, str]]):
		super().__init__(requestor)
		self.headers = headers

	def request(self, request: Request, timeout: Optional[int] = None) -> Response:
		if self.headers:
			h = request.headers
			h.update({**self.headers, **h})
		return self.requestor.request(request, timeout)
