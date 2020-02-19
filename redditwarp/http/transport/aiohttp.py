"""Transport adapter for aiohttp."""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from ..request import Request

import asyncio
import aiohttp

from .base_session_async import BaseSession
from .. import exceptions
from .. import payload
from ..response import Response

_PAYLOAD_DISPATCH_TABLE = {
	type(None): lambda y: {},
	payload.Raw: lambda y: {'data': y.data},
	payload.FormData: lambda y: {'data': y.data},
	payload.MultiPart: lambda y: {'files': y.data},
	payload.Text: lambda y: {'data': y.text},
	payload.JSON: lambda y: {'json': y.json},
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
		kwargs_x = _PAYLOAD_DISPATCH_TABLE[type(r.payload)](r.payload)
		kwargs.update(kwargs_x)

		try:
			async with self.session.request(**kwargs) as resp:
				content = await resp.content.read()
		except asyncio.TimeoutError as e:
			raise exceptions.TimeoutError(e) from e
		except Exception as e:
			raise exceptions.TransportError(e) from e

		return Response(
			status=resp.status,
			headers=resp.headers,
			data=content,
			request=r,
			transport_response=resp,
		)

	async def close(self) -> None:
		await self.session.close()

def new_session() -> Session:
	connector = aiohttp.TCPConnector(limit=20)
	se = aiohttp.ClientSession(connector=connector)
	return Session(se)
