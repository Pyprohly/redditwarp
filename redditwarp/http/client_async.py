
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Any, Optional, Dict
	from ..auth import ClientCredentials, Token, AuthorizationGrant
	from .response import Response

import sys
from asyncio import sleep

from ..auth.client_async import TokenClient
from ..auth import TOKEN_ENDPOINT, RESOURCE_BASE_URL
from .transport import aiohttp as t_aiohttp
from .request import Request
from .authorizer_async import Authorizer, Authorized
from .ratelimiter_async import RateLimited
from .exceptions import HTTPResponseError, http_error_response_classes
from .. import __about__

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
	) -> None:
		self.session = t_aiohttp.new_session()
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

		u = [
			(__about__.__title__, __about__.__version__),
			('Python', '.'.join(map(str, sys.version_info[:2]))),
			(t_aiohttp.name, t_aiohttp.version_string),
		]
		self.user_agent = ' '.join('/'.join(i) for i in u)

	async def request(self, verb: str, path: str, *, params: Optional[Dict[str, str]] = None,
			data: Any = None, headers: Dict[str, str] = None, timeout: int = 8) -> Response:
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

	async def close(self):
		await self.session.close()
		await self._token_session.close()

HTTPClient = RedditHTTPClient
