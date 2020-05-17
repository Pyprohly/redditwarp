
import __main__  # type: ignore[import]

from . import http
from . import auth
from .core.http_client_sync import HTTPClient
from .http.misc import json_loads_response
from .auth import ClientCredentials, Token, auto_grant_factory
from .util import get_praw_config
from .http.transport.requests import new_session
from .auth.token_obtainment_client_sync import TokenObtainmentClient
from .auth.const import TOKEN_OBTAINMENT_URL
from .core.authorizer_sync import Authorizer, Authorized
from .core.ratelimited_sync import RateLimited
from .core.default_headers_predisposed_sync import DefaultHeadersPredisposed
from .exceptions import (
	AuthError,
	APIError,
	HTTPStatusError,
	get_response_content_error,
	raise_for_json_layout_content_error,
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
	def from_praw_config(cls, site_name=''):
		config = get_praw_config()
		section_name = site_name or config.default_section
		try:
			section = config[section_name]
		except KeyError:
			class StrReprStr(str):
				def __repr__(self):
					return str(self)
			empty = not any(s.values() for s in config.values())
			msg = f"No section {section_name!r} in{' empty' if empty else ''} config"
			raise KeyError(StrReprStr(msg)) from None

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

		No token client means `self.http.authorizer.token_client` is `None`.

		When the token becomes invalid you'll need to deal with the 401 Unauthorized
		exception that will be thrown upon making requests. You can use the
		:meth:`set_access_token` method to assign a new token.

		Parameters
		----------
		t: str
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
			If you've registered an installed app (hence using the :class:`~.InstalledClient`
			grant type) you won't be given a client secret. The Reddit docs say to use an
			empty string in this case.
		refresh_token: Optional[str]
		access_token: Optional[str]
			Initialize the client :class:`~.Authorizer` with an access token.
			The token will continue to be used until the server indicates
			an invalid token, in which case the configured grant will used to
			exchange for a new access token.
		username: Optional[str]
			Reddit account username.
			Must be used with :param:`password`.
			Ignored if :param:`refresh_token` is used.
		password: Optional[str]
			Reddit account password.
			Must be used with :param:`username`.
			Ignored if :param:`refresh_token` is used.
		grant: Optional[:class:`~.AuthorizationGrant`]
			Explicitly input a grant. Use this parameter if you need to limit
			authorization scopes, or if you need to use the Installed Client grant type.

		A :class:`~.ClientCredentialsGrant` grant will be configured if only :param:`client_id`
		and :param:`client_secret` are specified.

		Raises
		------
		TypeError
			If grant credential parameters were specified and the `grant` parameter was used.
		ValueError
			You used :param:`username` without :param:`password` or vice versa.
		"""
		grant_creds = (refresh_token, username, password)
		if grant is None:
			grant = auto_grant_factory(*grant_creds)
			if grant is None:
				raise ValueError("couldn't automatically create a grant from the provided credentials")
		elif any(grant_creds):
			raise TypeError("you shouldn't pass grant credentials if you explicitly provide a grant")

		token = None if access_token is None else Token(access_token)
		session = new_session()
		authorizer = Authorizer(token, None)
		requestor = RateLimited(Authorized(session, authorizer))
		http = HTTPClient(requestor, session, authorizer=authorizer)
		authorizer.token_client = TokenObtainmentClient(
			DefaultHeadersPredisposed(session, http.default_headers),
			TOKEN_OBTAINMENT_URL,
			ClientCredentials(client_id, client_secret),
			grant,
		)
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
		s = str(s)
		ua = self.http.USER_AGENT_STRING_HEAD
		if s is not None:
			ua += ' Bot -- ' + s
		self.http.user_agent = ua

	def request(self, verb, path, *, params=None, payload=None,
			data=None, json=None, headers=None, timeout=8, auxiliary=None):
		try:
			resp = self.http.request(verb, path, params=params, payload=payload,
					data=data, json=json, headers=headers, timeout=timeout, auxiliary=auxiliary)

		except auth.exceptions.ResponseException as e:
			self.last_response = e.response
			raise AuthError(response=e.response) from e
		except http.exceptions.ResponseException as e:
			self.last_response = e.response
			raise APIError(response=e.response) from e

		self.last_response = resp

		try:
			data = json_loads_response(resp)
		except ValueError:
			raise get_response_content_error(resp) from None

		raise_for_json_layout_content_error(resp, data)
		raise_for_variant1_reddit_api_error(resp, data)
		raise_for_variant2_reddit_api_error(resp, data)

		try:
			resp.raise_for_status()
		except http.exceptions.StatusCodeException as e:
			raise HTTPStatusError(response=resp) from e

		return data

	def set_access_token(self, access_token):
		"""Manually set the access token.

		Tip: the currently set access token can be found with
		`self.http.authorizer.token.access_token`

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

	def __class_getitem__(cls, other):
		if not isinstance(other, str):
			raise TypeError
		if hasattr(__main__, '__file__'):
			raise RuntimeError("instantiating Client through __class_getitem__ can only be done interactively")
		return cls.from_praw_config(other)
