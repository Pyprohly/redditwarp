
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Any, Optional, Dict
	from ..auth import ClientCredentials, Token, AuthorizationGrant
	from .tranport.base_session_async import BaseSession
	from .response import Response

import sys
from asyncio import sleep

from .transport import aiohttp as t_aiohttp
from ..auth.client_async import TokenClient
from ..auth import TOKEN_ENDPOINT, RESOURCE_BASE_URL
from .authorizer_async import Authorizer, Authorized
from .ratelimiter_async import RateLimited
from .request import Request
from .exceptions import HTTPResponseError, http_error_response_classes
from .. import __about__

_u = [
	(__about__.__title__, __about__.__version__),
	('Python', '.'.join(map(str, sys.version_info[:2]))),
	(t_aiohttp.name, t_aiohttp.version_string),
]
DEFAULT_USER_AGENT_STRING = ' '.join('/'.join(i) for i in _u)


class RedditHTTPClient:
	@property
	def user_agent(self):
		return self.session.headers['User-Agent']

	@user_agent.setter
	def user_agent(self, value):
		self.session.headers['User-Agent'] = value
		self._token_session.headers['User-Agent'] = value

	def __init__(self,
		client_credentials: ClientCredentials,
		grant: AuthorizationGrant,
		token: Optional[Token],
		session: Optional[BaseSession] = None,
	) -> None:
		self.session = t_aiohttp.new_session() if session is None else session
		self.session.params['raw_json'] = '1'

		self._token_session = t_aiohttp.new_session()
		self.authorizer = Authorizer(
			TokenClient(
				self._token_session,
				TOKEN_ENDPOINT,
				client_credentials,
				grant,
			),
			token,
		)

		self.requestor = RateLimited(Authorized(self.session, self.authorizer))

		self.resource_base_url = RESOURCE_BASE_URL
		self.user_agent = DEFAULT_USER_AGENT_STRING

	async def __aenter__(self) -> RedditHTTPClient:
		return self

	async def __aexit__(self,
		exc_type: Optional[Type[BaseException]],
		exc_value: Optional[BaseException],
		traceback: Optional[TracebackType],
	) -> Optional[bool]:
		await self.close()

	async def request(self, verb: str, path: str, *, params: Optional[Dict[str, str]] = None,
			data: Any = None, headers: Optional[Dict[str, str]] = None, timeout: int = 8) -> Response:
		url = self.resource_base_url + path
		r = Request(verb, url, params=params, data=data, headers=headers)

		response = None
		status = -1
		for i in range(5):
			response = await self.requestor.request(r, timeout)
			status = response.status

			if 200 <= status < 300:
				return response

			if status in (500, 502):
				await sleep(2**i + 1)
				continue

			break

		clss = http_error_response_classes.get(status, HTTPResponseError)
		raise clss(response)

	async def close(self) -> None:
		await self.session.close()
		await self._token_session.close()

HTTPClient = RedditHTTPClient
