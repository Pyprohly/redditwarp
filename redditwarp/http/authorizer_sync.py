
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from ..auth.token_obtainment_client_sync import TokenObtainmentClient
	from ..auth.token import TokenResponse
	from .requestor_sync import Requestor
	from .request import Request
	from .response import Response

import time

from .requestor_sync import RequestorDecorator
from ..auth.token import Token, make_bearer_token

class Authorizer:
	"""Knows how to authorize requests."""

	def __init__(self, token: Optional[Token] = None,
			token_client: Optional[TokenObtainmentClient] = None,
			expiry_skew: int = 30) -> None:
		self.token = token
		self.token_client = token_client
		self.expiry_skew = expiry_skew
		self.expiry_time: Optional[int] = None
		self.expires_in_fallback: int = 3600
		self.last_token_response: Optional[TokenResponse] = None

	def token_expired(self) -> bool:
		if self.expiry_time is None:
			return False
		return self.current_time() > self.expiry_time

	def can_renew_token(self) -> bool:
		return self.token_client is not None

	def renew_token(self) -> Token:
		if self.token_client is None:
			raise RuntimeError('a new token was requested but no token client is assigned')

		tr = self.token_client.fetch_token_response()
		self.last_token_response = tr
		t = make_bearer_token(tr)
		self.token = t

		expires_in = self.expires_in_fallback if t.expires_in is None else t.expires_in
		self.expiry_time = int(self.current_time()) + expires_in - self.expiry_skew

		return t

	def maybe_renew_token(self) -> Optional[Token]:
		"""Attempt to renew the token if it is unavailable or has expired."""
		if (self.token is None) or self.token_expired():
			return self.renew_token()
		return None

	def prepare_request(self, request: Request) -> None:
		if self.token is None:
			raise RuntimeError('no token is set')
		request.headers['Authorization'] = '{0.TOKEN_TYPE} {0.access_token}'.format(self.token)

	def current_time(self) -> float:
		return time.monotonic()

	def remaining_time(self) -> Optional[int]:
		if self.expiry_time is None:
			return None
		return self.expiry_time - int(self.current_time())


class Authorized(RequestorDecorator):
	"""Used to perform requests to endpoints that require authorization."""

	def __init__(self, requestor: Requestor, authorizer: Authorizer) -> None:
		super().__init__(requestor)
		self.authorizer = authorizer

	def request(self, request: Request, timeout: Optional[int] = None) -> Response:
		self.authorizer.maybe_renew_token()
		self.authorizer.prepare_request(request)
		response = self.requestor.request(request, timeout)

		if response.status == 401 and self.authorizer.can_renew_token():
			self.authorizer.renew_token()
			self.authorizer.prepare_request(request)
			response = self.requestor.request(request, timeout)

		return response
