
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Type, Any, Optional, Mapping, Dict
	from types import TracebackType
	from .transport.base_session_async import BaseSession
	from .authorizer_async import Authorizer
	from .requestor_async import Requestor
	from .response import Response
	from .payload import Payload

import sys
from asyncio import sleep

from .transport import transport_reg
from ..auth.const import RESOURCE_BASE_URL
from .request import Request
from .. import __about__
from .payload import make_payload

transport_info = transport_reg['aiohttp']

class RedditHTTPClient:
	TIMEOUT = 8
	USER_AGENT_STRING_HEAD = (
		f"{__about__.__title__}/{__about__.__version__} "
		f"Python/{'{0[0]}.{0[1]}'.format(sys.version_info)} "
		f"{transport_info.name}/{transport_info.version_string}"
	)

	@property
	def default_headers(self):
		return self._default_headers

	@property
	def user_agent(self):
		return self._default_headers['User-Agent']

	@user_agent.setter
	def user_agent(self, value):
		self._default_headers['User-Agent'] = value

	def __init__(self,
		requestor: Requestor,
		session: BaseSession,
		*,
		default_headers: Optional[Mapping[str, str]] = None,
		authorizer: Optional[Authorizer],
	) -> None:
		self.requestor = requestor
		self.session = session
		self._default_headers = {} if default_headers is None else default_headers
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
		headers.setdefault('User-Agent', self.user_agent)

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
