
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional, Dict
	from ..auth import ClientCredentials, Token
	from .response import Response
	from .requestor import RequestorDecorator

import sys
import requests

from ..auth import TokenClient, TOKEN_ENDPOINT, RESOURCE_BASE_URL
from .request import Request
from .transport.requests import Session
from .authorizer import Authorizer, Authorized

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
		session.params['raw_json'] = '1'

		self._token_session = Session()
		self.authorizer = authorizer = Authorizer(
			TokenClient(
				self._token_session,
				TOKEN_ENDPOINT,
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
		return self.requestor.request(r, timeout)
