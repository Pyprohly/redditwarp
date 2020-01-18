
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from ..auth.client_sync import TokenClient
	from .requestor_sync import Requestor
	from .request import Request
	from .response import Response
	from .token import TokenResponse

import time

from .requestor_sync import RequestorDecorator
from ..auth import Token

class Authorizer:
	"""Knows how to authorize requests."""

	def __init__(self, token_client: TokenClient, token: Optional[Token] = None, expiry_skew: int = 30) -> None:
		self.token_client = token_client
		self.token = token
		self.expiry_skew = expiry_skew
		self.expiry_time: Optional[int] = None
		self.expires_in_fallback = 3600

	def token_expired(self) -> bool:
		if self.expiry_time is None:
			return False
		return self.current_time() > self.expiry_time

	def renew_token(self) -> Token:
		tr: TokenResponse = self.token_client.fetch_token()
		expires_in = tr.expires_in
		if expires_in is None:
			expires_in = self.expires_in_fallback

		self.expiry_time = int(self.current_time()) + expires_in - self.expiry_skew
		self.token = token = Token(
			access_token=tr.access_token,
			refresh_token=tr.refresh_token,
			expires_in=expires_in,
			scope=tr.scope,
		)
		return token

	def prepare(self):
		if (self.token is None) or self.token_expired():
			self.renew_token()

	def prepare_request(self, request: Request) -> None:
		request.headers['Authorization'] = '{0.token_type} {0.access_token}'.format(self.token)

	def current_time(self):
		return time.monotonic()

	def remaining_time(self) -> Optional[int]:
		if self.expiry_time is None:
			return None
		return self.expiry_time - int(self.current_time())


class Authorized(RequestorDecorator):
	"""Used to perform requests to endpoints that require authorization."""

	def __init__(self, requestor: Requestor, authorizer: Optional[Authorizer] = None) -> None:
		super().__init__(requestor)
		self.authorizer = authorizer

	def request(self, request: Request, timeout: Optional[int]) -> Response:
		self.prepare_request(request)
		response = self.requestor.request(request, timeout)
		if response.status == 401:
			self.authorizer.renew_token()
			response = self.requestor.request(request, timeout)
		return response

	def prepare_request(self, request: Request) -> None:
		if 'Authorization' not in request.headers:
			self.authorizer.prepare()
			self.authorizer.prepare_request(request)
