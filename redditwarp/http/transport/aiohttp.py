"""Transport adapter for aiohttp."""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .request import Request

import aiohttp

from .base_session_async import BaseSession
from .. import exceptions
from .. import payload
from ..response import Response

_PAYLOAD_DISPATCH_TABLE = {
	type(None): lambda data: {},
	payload.Raw: lambda data: dict(data=data),
	payload.FormData: lambda data: dict(data=data),
	payload.MultiPart: lambda data: dict(files=data),
	payload.Text: lambda data: dict(data=data),
	payload.JSON: lambda data: dict(json=data),
}


name = 'aiohttp'
version_string = aiohttp.__version__


class Session(BaseSession):
	def __init__(self, session: aiohttp.ClientSession) -> None:
		super().__init__()
		self.session = session

	async def request(self, request: Request, timeout: Optional[int] = 8) -> Response:
		self._prepare_request(request)

		r = request
		kwargs = {
			'method': r.verb,
			'url': r.url,
			'params': r.params,
			'headers': r.headers,
			'timeout': timeout,
		}
		kwargs_x = _PAYLOAD_DISPATCH_TABLE[type(r.data)](r.data)
		kwargs.update(kwargs_x)

		try:
			async with self.session.request(**kwargs) as resp:
				content = await resp.content.read()
		except Exception as exc:
			raise exceptions.TransportError(exc) from exc

		return Response(
			status=resp.status,
			headers=resp.headers,
			data=content,
			response=resp,
			request=r,
		)

	async def close(self) -> None:
		await self.session.close()

def new_session() -> Session:
	connector = aiohttp.TCPConnector(limit=20)
	se = aiohttp.ClientSession(connector=connector)
	return Session(se)
