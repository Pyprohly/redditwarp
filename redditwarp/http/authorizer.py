
import time

from .requestor import RequestorDecorator


class Authorizer:
	"""Knows how to authorize requests."""

	def __init__(self, token_client: TokenClient, expiry_skew: int = 60) -> None:
		self.token_client = token_client
		self.expiry_skew = expiry_skew
		self.expires_in: Optional[int] = None
		self.expires: Optional[int] = None
		self.token = None

	def token_expired(self, skew: Optional[int] = None) -> bool:
		if self.token is None:
			return True
		if skew is None:
			skew = self.expiry_skew
		if time.monotonic() + skew >= self.expires:
			return True
		return False

	def renew_token(self) -> Token:
		token_response: TokenResponse = self.token_client.fetch_token()
		self.expires_in = expires_in = token_response.expires_in
		self.expires = int(time.monotonic()) + expires_in
		self.token = token = Token(
			access_token=token_response.access_token,
			refresh_token=token_response.refresh_token,
			expires_in=expires_in,
		)
		return token

	def prepare_request(request: Request) -> None:
		if self.token_expired():
			self.renew_token()
		request.headers['Authorization'] = '{0.token_type} {0.access_token}'.format(self.token)


class Authorized(RequestorDecorator):
	"""A Requests Session wrapper class that holds credentials.

	This class is used to perform requests to API endpoints that require
	authorization. The :meth:`request` method handles adding authorization
	headers to the request and refreshing credentials when needed.

	Parameters
	----------
	credentials: :class:`warp.http.auth.credentials.Credentials`
		The credentials to apply to requests.
	requestor: Optional[:class:`~.Requestor`]
		The requestor used when making API requests.
	token_requestor: Optional[:class:`~.Requestor`]
		The requestor used for refreshing credentials.
	"""

	def __init__(self, requestor: Requestor, authorizer: Optional[Authorizer] = None):
		super().__init__(requestor)
		self.authorizer = Authorizer() if authorizer is None else authorizer

	def request(self, request, timeout=TIMEOUT):
		self.prepare_request(request)
		response = self.requestor.request(request)

		if response.status == 401:
			raise AssertionError('401 response')
			self.prepare_request(request)
			response = self.requestor.request(request)

		return response

	def prepare_request(self, request) -> None:
		self.authorizer.prepare_request(request)
