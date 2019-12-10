
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .auth.client import TokenClient

import time

from .requestor import RequestorDecorator
from .auth.token import Token

TIMEOUT = 8

class Authorizer:
	"""Knows how to authorize requests."""

	def __init__(self, token_client: TokenClient, token: Optional[Token] = None, expiry_skew: int = 30) -> None:
		self.token_client = token_client
		self.expiry_skew = expiry_skew
		self.expiry_time = 0
		self.expires_in_fallback = 3600
		self.token: Optional[Token] = None

	def token_expired(self) -> bool:
		return time.monotonic() > self.expiry_time

	def renew_token(self) -> Token:
		tr: TokenResponse = self.token_client.fetch_token()
		expires_in = tr.expires_in
		if expires_in is None:
			expires_in = self.expires_in_fallback

		self.expiry_time = int(time.monotonic()) + expires_in - self.expiry_skew
		self.token = token = Token(
			access_token=tr.access_token,
			refresh_token=tr.refresh_token,
			expires_in=expires_in,
			scope=tr.scope,
		)
		return token

	def prepare_request(self, request: Request) -> None:
		if (self.token is None) or self.token_expired():
			self.renew_token()
		request.headers['Authorization'] = '{0.token_type} {0.access_token}'.format(self.token)

	def remaining_time(self) -> int:
		return self.expiry_time - int(time.monotonic())


class Authorized(RequestorDecorator):
	"""Used to perform requests to endpoints that require authorization."""

	def __init__(self, requestor: Requestor, authorizer: Optional[Authorizer] = None) -> None:
		super().__init__(requestor)
		self.authorizer = Authorizer() if authorizer is None else authorizer

	def request(self, request: Request, timeout: int = TIMEOUT) -> Response:
		print('**********')
		print(request.headers)
		print('**********')
		self.prepare_request(request)
		print('**********')
		print(request.headers)
		print('**********')
		response = self.requestor.request(request, timeout=timeout)

		if response.status == 401:
			raise AssertionError('401 response')
			self.prepare_request(request)
			response = self.requestor.request(request, timeout=timeout)

		return response

	def prepare_request(self, request: Request) -> None:
		self.authorizer.prepare_request(request)
