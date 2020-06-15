
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
if TYPE_CHECKING:
	from .request import Request
	from .response import Response

class Requestor:
	async def request(self, request: Request, *, timeout: Optional[float] = None,
			aux_info: Optional[Mapping] = None) -> Response:
		raise NotImplementedError

class RequestorDecorator(Requestor):
	def __init__(self, requestor: Requestor) -> None:
		self.requestor = requestor

	async def request(self, request: Request, *, timeout: Optional[float] = None,
			aux_info: Optional[Mapping] = None) -> Response:
		return await self.requestor.request(request, timeout=timeout, aux_info=aux_info)
