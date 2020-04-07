
import __main__  # type: ignore[import]

from . import http
from . import auth
from .http.client_async import HTTPClient
from .http.util import json_loads_response
from .auth import ClientCredentials, Token, auto_grant_factory
from .util import load_praw_config
from .http.transport.aiohttp import new_session
from .auth.token_obtainment_client_async import TokenObtainmentClient
from .auth import TOKEN_OBTAINMENT_ENDPOINT
from .http.authorizer_async import Authorizer, Authorized
from .http.ratelimiter_async import RateLimited
from .http.apply_headers_async import ApplyHeaders
from .exceptions import (
	ResponseException,
	HTTPStatusError,
	get_response_content_error,
	raise_for_json_response_content_error,
	raise_for_variant1_reddit_api_error,
	raise_for_variant2_reddit_api_error,
)
#from .api import SiteProcedures

class ClientCore:
	@classmethod
	def from_http(cls, http):
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
		aphe = ApplyHeaders(session, None)
		authorizer = Authorizer(
			token,
			TokenObtainmentClient(
				aphe,
				TOKEN_OBTAINMENT_ENDPOINT,
				client_credentials,
				grant,
			),
		)
		requestor = RateLimited(Authorized(session, authorizer))
		http = HTTPClient(requestor, session, authorizer=authorizer)
		aphe.headers = http.default_headers
		self._init(http)

	def _init(self, http):
		self.http = http
		self.last_response = None

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc_value, traceback):
		await self.close()

	async def close(self):
		await self.http.close()

	def set_user_agent(self, s):
		ua = self.http.USER_AGENT_STRING_HEAD
		if s is not None:
			ua += ' -- ' + s
		self.http.user_agent = ua

	async def request(self, verb, path, *, params=None,
			payload=None, data=None, json=None, headers=None, timeout=8):
		try:
			resp = await self.http.request(verb, path, params=params,
					payload=payload, data=data, json=json, headers=headers, timeout=timeout)

		except auth.exceptions.ResponseException as e:
			self.last_response = e.response
			raise ResponseException(e.response) from e
		except http.exceptions.ResponseException as e:
			self.last_response = e.response
			raise ResponseException(e.response) from e

		self.last_response = resp

		try:
			data = json_loads_response(resp)
		except ValueError:
			raise get_response_content_error(resp) from None

		raise_for_json_response_content_error(resp, data)
		raise_for_variant1_reddit_api_error(resp, data)
		raise_for_variant2_reddit_api_error(resp, data)

		try:
			resp.raise_for_status()
		except http.exceptions.StatusCodeException as e:
			raise HTTPStatusError(resp) from e

		return data

	def set_access_token(self, access_token):
		self.http.authorizer.token = Token(access_token)

class Client(ClientCore):
	def _init(self, http):
		super()._init(http)
		self.api = ...#SiteProcedures(self)
		self.fetch = self.api.fetch

	def __class_getitem__(cls, name):
		if not isinstance(name, str):
			raise TypeError
		if hasattr(__main__, '__file__'):
			raise RuntimeError("instantiating Client through __class_getitem__ can only be done interactively")
		return cls.from_praw_config(name)
