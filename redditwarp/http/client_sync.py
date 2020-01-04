
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Any, Optional, Dict
	from ..auth import ClientCredentials, Token, AuthorizationGrant
	from .response import Response

import sys
import time

import requests

from ..auth.client_sync import TokenClient
from ..auth import TOKEN_ENDPOINT, RESOURCE_BASE_URL
from .request import Request
from .transport.requests import Session
from .authorizer_sync import Authorizer, Authorized
from .ratelimiter_sync import RateLimited
from .exceptions import HTTPResponseError, http_error_response_classes

class HTTPClient:
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
		self.session = Session()
		self.session.params['raw_json'] = '1'

		self._token_session = Session()
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
		self.user_agent = 'RedditWarp/{0} Python/{1[0]}.{1[1]} requests/{2}' \
				.format('alpha', sys.version_info, requests.__version__)

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

			if status == 429:
				assert False
				raise AssertionError('429 response')

			if status in (500, 502):
				time.sleep(2**i + 1)
				continue

			break

		clss = http_error_response_classes.get(status, HTTPResponseError)
		raise clss(response)

	def close(self):
		self.session.close()
		self._token_session.close()
