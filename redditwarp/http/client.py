
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict
if TYPE_CHECKING:
	from .response import Response
	from .requestor import RequestorDecorator

import sys
import requests

from .request import Request
from .transport.requests import Session

from ..auth.provider import Provider
from ..auth.credentials import ClientCredentials
from ..authorizer import Authorized, Authorizer
from ..auth.provider import Provider
from ..auth.credentials import ClientCredentials
from ..auth.grant import auto_grant_factory
from ..auth.client import TokenClient
from ..auth.token import Token
from ..authorizer import Authorized, Authorizer

AUTHORIZATION_ENDPOINT = 'https://www.reddit.com/api/v1/authorize'
TOKEN_ENDPOINT = 'https://www.reddit.com/api/v1/access_token'
RESOURCE_BASE_URL = 'https://oauth.reddit.com'
DEFAULT_PROVIDER = Provider(AUTHORIZATION_ENDPOINT, TOKEN_ENDPOINT, RESOURCE_BASE_URL)

class HTTPClient:
	@property
	def user_agent(self):
		return self.session.headers['User-Agent']

	@user_agent.setter
	def user_agent(self, value):
		self.session.headers['User-Agent'] = value
		self._token_session.headers['User-Agent'] = value

	@property
	def token_interceptor(self):
		return self._token_interceptor

	def __init__(self,
		client_credentials: ClientCredentials,
		grant: AuthorizationGrant,
		token: Optional[Token],
		token_interceptor: Optional[RequestorDecorator] = None,
		interceptor: Optional[RequestorDecorator] = None,
	) -> None:
		self.session = session = Session()
		session.headers['raw_json'] = '1'

		self._token_session = Session()
		self.authorizer = authorizer = Authorizer(
			TokenClient(
				self._token_session,
				DEFAULT_PROVIDER,
				client_credentials,
				grant,
			),
			token,
		)

		#self._requestor_stack_bottom = 
		# Ratelimited(Retryable(Session()))
		self.requestor = Authorized(session, authorizer)
		self.resource_base_url = RESOURCE_BASE_URL
		self.user_agent = 'RedditWarp/{0} Python/{1[0]}.{1[1]} requests/{2}' \
				.format('alpha', sys.version_info, requests.__version__)

	def request(self, verb: str, path: str, *, params: Optional[Dict[str, str]] = None,
			data: Any = None, headers: Dict[str, str] = None, timeout: int = 8) -> Response:
		url = self.resource_base_url + path
		r = Request(verb, url, params=params, data=data, headers=headers)
		return self.requestor.request(r)
