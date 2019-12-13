
from .http import HTTPClient
from .http.authorizer import Authorizer
from .http.transport.requests import Session

from .auth.credentials import ClientCredentials
from .auth.grant import auto_grant_factory
from .auth.client import TokenClient
from .auth.token import Token
from .http.authorizer import Authorized, Authorizer


class Client:
	"""The gateway to interacting with the Reddit API."""

	@classmethod
	def from_http(cls, http):
		"""Alternative constructor. For testing purposes. For advanced uses.

		Parameters
		----------
		http: Optional[:class:`HTTPClient`]
		"""
		self = cls.__new__(cls)
		self._init(http)
		return self

	def __init__(self,
			client_id, client_secret, refresh_token=None,
			access_token=None, *, username=None, password=None,
			grant=None, token_interceptor=None, interceptor=None):
		"""
		Parameters
		----------
		client_id: str
		client_secret: str
			Required for all grant types except for the (Reddit-specific) Installed Client grant type.
			If you're using an Installed Client grant you may set this to an empty string.
		refresh_token: Optional[str]
		access_token: Optional[str]
		username: Optional[str]
		password: Optional[str]
		grant: Optional[:class`AuthorizationGrant`]
			Configure the authorization grant explicitly. You'd use this parameter if you need
			control over authorization scopes, or if you need to use the Installed Client grant type.
		token_interceptor: Optional[:class`RequestorDecorator`]
			Wrap the underlying session object with this object.
			The final opportunity to modify outgoing requests, or capturing incoming server responses
			The 'final call' to intercept and potentially modify requests. You can also use this to capture incoming server responses
		interceptor: Optional[:class`RequestorDecorator`]
			Similar to :param:`token_interceptor` but for requests that are made to the resource server.

		Raises
		------
		TypeError
			If bare credentials were provided and the `grant` parameter was used.
		"""
		auto_grant = (refresh_token, username, password)
		if any(auto_grant):
			if grant:
				raise TypeError('you should not pass grant credentials if you explicitly provide a grant')
			grant = auto_grant_factory(*auto_grant)
			if grant is None:
				assert False
				raise ValueError('could not automatically create an authorization grant from the provided grant credentials')

		cc = ClientCredentials(client_id, client_secret)
		token = Token(access_token) if access_token else None
		self._init(HTTPClient(cc, grant, token, token_interceptor, interceptor))

	def _init(self, http):
		self.http = http

	def request(self, verb, path, *, params=None, data=None, headers=None):
		return self.http.request(verb, path, params=params, data=data, headers=headers)
