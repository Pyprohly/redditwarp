
from .http import HTTPClient
from .http.client import DEFAULT_PROVIDER as _DEFAULT_PROVIDER
from .http.auth.grant import auto_grant_factory
from .http.authorizer import Authorizer
from .http.transport.requests import Session

from .http.auth.provider import Provider
from .http.auth.credentials import ClientCredentials
from .http.auth.grant import auto_grant_factory
from .http.auth.client import TokenClient
from .http.auth.token import Token
from .http.authorizer import Authorized, Authorizer


class Client:
	"""The gateway to interacting with the Reddit API."""

	@classmethod
	def from_http(cls, http):
		"""For testing purposes, or advanced use.

		Parameters
		----------
		http: Optional[:class:`BaseHTTPClient`]
			Use a custom HTTPClient.
		"""
		self = cls.__new__(cls)
		self._init(http)
		return self

	def __init__(self,
			client_id=None, client_secret=None, refresh_token=None,
			access_token=None, *, username=None, password=None,
			authorizer=None, session=None):
		"""
		Parameters
		----------
		client_id: Optional[str]
			Client ID.
		client_secret: Optional[str]
			Client secret.
		refresh_token: Optional[str]
		access_token: Optional[str]
		username: Optional[str]
		password: Optional[str]


		'''
		authorizer: Optional[:class`Authorizer`]
			Explicit authorization configuration.
			For instance if you want to limit scopes.
		session: Optional[:class:`Session`]
			Use this if you need to intercept HTTP requests.

		'''
		grant: Optional[:class`AuthorizationGrant`]
			Configure the authorization grant explicitly. You'd use this parameter if you need
			control over authorization scopes, or if you need to use the Installed Client grant type.
		token_interceptor: Optional[:class`RequestorDecorator`]
			Wrap the underlying session object with this object.
			The final opportunity to modify outgoing requests, or capturing incoming server responses
			The 'final call' to intercept and potentially modify requests. You can also use this to capture incoming server responses
		interceptor: Optional[:class`RequestorDecorator`]
			Similar to :param:`token_interceptor` but for requests that are made to the resource server.
			There should be no need to use this (RedditWarp already does logging).

		Raises
		------
		TypeError
			If direct credentials were provided but 
		"""
		creds = (client_id, client_secret, refresh_token, username, password)
		if authorizer:
			if any(creds):
				raise TypeError("you should not pass direct credentials if `authorizer` is used")
		else:
			grant = auto_grant_factory(*creds)
			if grant is None:
				raise ValueError('could not automatically make an authorization grant from the provided credentials.')

			if session is None:
				session = Session()

			authorizer = Authorizer(
				TokenClient(
					session,
					_DEFAULT_PROVIDER,
					ClientCredentials(client_id, client_secret),
					grant,
				),
				Token(access_token) if access_token else None,
			)

		if session is None:
			session = Session()

		self._init(HTTPClient(session, authorizer))

	def _init(self, http):
		self.http = http

	def request(self, verb, path, *, params=None, data=None, headers=None):
		return self.http.request(verb, path, params=params, data=data, headers=headers)
