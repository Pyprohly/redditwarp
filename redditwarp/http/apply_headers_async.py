
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
if TYPE_CHECKING:
	from .requestor_async import Requestor
	from .request import Request
	from .response import Response

from .requestor_async import RequestorDecorator

class ApplyHeaders(RequestorDecorator):
	def __init__(self, requestor: Requestor, headers: Optional[Mapping[str, str]]):
		super().__init__(requestor)
		self.headers = headers

	async def request(self, request: Request, timeout: Optional[int] = None) -> Response:
		if self.headers:
			h = request.headers
			h.update({**self.headers, **h})
		return await self.requestor.request(request, timeout)
