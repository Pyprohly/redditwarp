
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Any, Optional, Dict
	from ..auth import ClientCredentials, Token, AuthorizationGrant
	from .response import Response

import sys
from time import sleep

from ..auth.client_sync import TokenClient
from ..auth import TOKEN_ENDPOINT, RESOURCE_BASE_URL
from .transport import requests as t_requests
from .request import Request
from .authorizer_sync import Authorizer, Authorized
from .ratelimiter_sync import RateLimited
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
		self.session = t_requests.new_session()
		self.session.params['raw_json'] = '1'

		self._token_session = t_requests.new_session()
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
			(t_requests.name, t_requests.version_string),
		]
		self.user_agent = ' '.join('/'.join(i) for i in u)

	def __enter__(self) -> RedditHTTPClient:
		return self

	def __exit__(self,
		exc_type: Optional[Type[BaseException]],
		exc_value: Optional[BaseException],
		traceback: Optional[TracebackType],
	) -> Optional[bool]:
		self.close()

	def request(self, verb: str, path: str, *, params: Optional[Dict[str, str]] = None,
			data: Any = None, headers: Dict[str, str] = None, timeout: int = 8) -> Response:
		url = self.resource_base_url + path
		r = Request(verb, url, params=params, data=data, headers=headers)

		response = None
		status = -1
		for i in range(5):
			response = self.requestor.request(r, timeout)
			status = response.status

			if 200 <= status < 300:
				return response

			if status in (500, 502):
				sleep(2**i + 1)
				continue

			break

		clss = http_error_response_classes.get(status, HTTPResponseError)
		raise clss(response)

	def close(self) -> None:
		self.session.close()
		self._token_session.close()

HTTPClient = RedditHTTPClient
