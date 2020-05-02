
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
if TYPE_CHECKING:
	from ..http.requestor_sync import Requestor
	from ..http.request import Request
	from ..http.response import Response

from ..http.requestor_sync import RequestorDecorator

class DefaultHeaderReceptive(RequestorDecorator):
	def __init__(self, requestor: Requestor, headers: Optional[Mapping[str, str]]):
		super().__init__(requestor)
		self.headers = headers

	def request(self, request: Request, *, timeout: Optional[float] = None,
			auxiliary: Optional[Mapping] = None) -> Response:
		if self.headers:
			h = request.headers
			h.update({**self.headers, **h})
		return self.requestor.request(request, timeout=timeout, auxiliary=auxiliary)
