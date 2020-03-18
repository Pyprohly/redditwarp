
import __main__

from .http.client_async import HTTPClient
from .http.util import json_loads_response
from .auth import ClientCredentials, Token, auto_grant_factory
from .util import load_praw_config
from .http.transport.aiohttp import new_session
from .auth.client_async import TokenClient
from .auth import TOKEN_ENDPOINT
from .http.authorizer_async import Authorizer, Authorized
from .http.ratelimiter_async import RateLimited
from .exceptions import parse_reddit_error_items, new_reddit_api_error, BadJSONLayout
#from .api import SiteProcedures

class Client:
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
		http = HTTPClient(requestor, session, authorizer)
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
		authorizer = Authorizer(
			token,
			TokenClient(
				session,
				TOKEN_ENDPOINT,
				client_credentials,
				grant,
			),
		)
		requestor = RateLimited(Authorized(session, authorizer))
		http = HTTPClient(requestor, session, authorizer)
		self._init(http)

	def _init(self, http):
		self.http = http

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
		resp = await self.http.request(verb, path, params=params,
				payload=payload, data=data, json=json, headers=headers, timeout=timeout)
		d = json_loads_response(resp)
		if {'jquery', 'success'} <= d.keys():
			raise BadJSONLayout(resp, d)
		error_list = parse_reddit_error_items(d)
		if error_list is not None:
			raise new_reddit_api_error(resp, error_list)
		resp.raise_for_status()
		return d

	def set_access_token(self, access_token):
		self.http.authorizer.token = Token(access_token)

ClientCore = Client

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
