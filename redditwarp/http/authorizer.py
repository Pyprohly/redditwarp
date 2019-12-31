
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from ..auth.client import TokenClient
	from .requestor import Requestor
	from .request import Request
	from .response import Response

import time

from .requestor import RequestorDecorator
from ..auth import Token

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
		self.authorizer = authorizer or Authorizer()

	def request(self, request: Request, timeout: Optional[int]) -> Response:
		self.prepare_request(request)
		response = self.requestor.request(request, timeout)

		if response.status == 401:
			self.authorizer.renew_token()

			response = self.requestor.request(request, timeout)
			if response.status == 401:
				# ! Raise an HTTP level exception
				raise AssertionError('401 response')

		return response

	def prepare_request(self, request: Request) -> None:
		if 'Authorization' not in request.headers:
			self.authorizer.prepare_request(request)
