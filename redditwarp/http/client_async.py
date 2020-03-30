
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Type, Any, Optional, Dict
	from types import TracebackType
	from .transport.base_session_async import BaseSession
	from .authorizer_async import Authorizer
	from .requestor_async import Requestor
	from .response import Response
	from .payload import Payload

import sys
from asyncio import sleep

from .transport import transport_reg
from ..auth import RESOURCE_BASE_URL
from .request import Request
from .. import __about__
from .payload import make_payload

transport_info = transport_reg['aiohttp']

class RedditHTTPClient:
	TIMEOUT = 8
	USER_AGENT_STRING_HEAD = (
		f"{__about__.__title__}/{__about__.__version__} "
		f"Python/{'{0[0]}.{0[1]}'.format(sys.version_info)} "
		f"{transport_info.name}/{transport_info.version_string} "
		"Bot"
	)

	def __init__(self,
		requestor: Requestor,
		session: BaseSession,
		authorizer: Optional[Authorizer],
	) -> None:
		self.requestor = requestor
		self.session = session
		self.authorizer = authorizer
		self.resource_base_url = RESOURCE_BASE_URL
		self.user_agent = self.USER_AGENT_STRING_HEAD

	async def __aenter__(self):
		return self

	async def __aexit__(self,
		exc_type: Optional[Type[BaseException]],
		exc_value: Optional[BaseException],
		traceback: Optional[TracebackType],
	) -> Optional[bool]:
		await self.close()
		return None

	async def request(self,
		verb: str,
		path: str,
		*,
		params: Optional[Dict[str, str]] = None,
		payload: Optional[Payload] = None,
		data: Any = None,
		json: Any = None,
		headers: Optional[Dict[str, str]] = None,
		timeout: int = TIMEOUT,
	) -> Response:
		url = self.resource_base_url + path
		payload = make_payload(payload, data, json)
		params = {} if params is None else params
		headers = {} if headers is None else headers

		params.setdefault('raw_json', '1')
		params.setdefault('api_type', 'json')

		headers['User-Agent'] = self.user_agent

		r = Request(verb, url, params=params, payload=payload, headers=headers)

		for i in range(5):
			response = await self.requestor.request(r, timeout)

			if response.status in (500, 502):
				await sleep(i**2)
				continue
			break

		return response

	async def close(self) -> None:
		await self.session.close()

HTTPClient = RedditHTTPClient
