
import __main__  # type: ignore[import]

from . import http
from .http.client_sync import HTTPClient
from .http.util import json_loads_response
from .auth import ClientCredentials, Token, auto_grant_factory
from .util import load_praw_config
from .http.transport.requests import new_session
from .auth.client_sync import TokenClient
from .auth import TOKEN_ENDPOINT
from .http.authorizer_sync import Authorizer, Authorized
from .http.ratelimiter_sync import RateLimited
from .http.apply_headers_sync import ApplyHeaders
from .exceptions import (
	HTTPStatusError,
	UnidentifiedResponseContentError,
	raise_for_content_response_error,
	raise_for_variant1_reddit_api_error,
	raise_for_variant2_reddit_api_error,
)
from .site_procedures import SiteProcedures

class ClientCore:
	"""The gateway to interacting with the Reddit API."""

	@classmethod
	def from_http(cls, http):
		"""A constructor for testing purposes or advanced uses.

		Parameters
		----------
		http: Optional[:class:`HTTPClient`]
		"""
		self = cls.__new__(cls)
		self._init(http)
		return self

	@classmethod
	def from_praw_config(cls, site_name='DEFAULT'):
		config = load_praw_config()
		section = config[site_name or 'DEFAULT']
		get = section.get
		self = cls(
			client_id=get('client_id'),
			client_secret=get('client_secret'),
			refresh_token=get('refresh_token'),
			username=get('username'),
			password=get('password'),
		)
		if 'user_agent' in section:
			self.set_user_agent(get('user_agent'))
		return self

	@classmethod
	def from_access_token(cls, access_token):
		"""Construct a Reddit client instance without a token client.

		No token client means `self.http.authorizer.token_client` will be `None`.

		When the token becomes invalid you'll need to deal with the 401
		Unauthorized exception that will be thrown on requests. You can
		use the :meth:`set_access_token` method to assign a new token.

		Parameters
		----------
		access_token: str
		"""
		token = Token(access_token)
		session = new_session()
		authorizer = Authorizer(token, None)
		requestor = RateLimited(Authorized(session, authorizer))
		http = HTTPClient(requestor, session, authorizer=authorizer)
		return cls.from_http(http)

	def __init__(self,
			client_id, client_secret, refresh_token=None,
			access_token=None, *, username=None, password=None,
			grant=None):
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
		grant: Optional[:class:`AuthorizationGrant`]
			Configure the authorization grant explicitly. You'd use this parameter if you need
			control over authorization scopes, or if you need to use the Installed Client grant type.

		Raises
		------
		TypeError
			If bare credentials were provided and the `grant` parameter was used.
		"""
		auto_grant_creds = (refresh_token, username, password)
		if grant is None:
			grant = auto_grant_factory(*auto_grant_creds)
			if grant is None:
				assert False
				raise ValueError('could not automatically create an authorization grant from the provided grant credentials')
		elif any(auto_grant_creds):
			raise TypeError("you shouldn't pass grant credentials if you explicitly provide a grant")

		client_credentials = ClientCredentials(client_id, client_secret)
		token = None if access_token is None else Token(access_token)
		session = new_session()
		ah = ApplyHeaders(session, None)
		authorizer = Authorizer(
			token,
			TokenClient(
				ah,
				TOKEN_ENDPOINT,
				client_credentials,
				grant,
			),
		)
		requestor = RateLimited(Authorized(session, authorizer))
		http = HTTPClient(requestor, session, authorizer=authorizer)
		ah.headers = http.default_headers
		self._init(http)

	def _init(self, http):
		self.http = http
		self.last_response = None

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

	def close(self):
		self.http.close()

	def set_user_agent(self, s):
		ua = self.http.USER_AGENT_STRING_HEAD
		if s is not None:
			ua += ' -- ' + s
		self.http.user_agent = ua

	def request(self, verb, path, *, params=None,
			payload=None, data=None, json=None, headers=None, timeout=8):
		resp = self.http.request(verb, path, params=params,
				payload=payload, data=data, json=json, headers=headers, timeout=timeout)
		self.last_response = resp

		try:
			data = json_loads_response(resp)
		except ValueError:
			raise UnidentifiedResponseContentError(resp) from None

		raise_for_content_response_error(resp, data)
		raise_for_variant1_reddit_api_error(resp, data)
		raise_for_variant2_reddit_api_error(resp, data)

		try:
			resp.raise_for_status()
		except http.exceptions.StatusCodeException as e:
			raise HTTPStatusError(resp) from e

		return data

	def set_access_token(self, access_token):
		"""Manually set the access token.

		Tip: to get the current access token use `self.http.authorizer.token.access_token`

		Parameters
		----------
		access_token: str
		"""
		self.http.authorizer.token = Token(access_token)

class Client(ClientCore):
	def _init(self, http):
		super()._init(http)
		self.api = SiteProcedures(self)
		self.fetch = self.api.fetch

	def __class_getitem__(cls, name):
		if not isinstance(name, str):
			raise TypeError
		if hasattr(__main__, '__file__'):
			raise RuntimeError("instantiating Client through __class_getitem__ can only be done interactively")
		return cls.from_praw_config(name)
