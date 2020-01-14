
from .http.client_sync import HTTPClient

from .auth import (
	ClientCredentials,
	Token,
	auto_grant_factory,
)

from .http.util import response_json


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
		else:
			if any(auto_grant_creds):
				raise TypeError("you shouldn't pass grant credentials if you explicitly provide a grant")

		cc = ClientCredentials(client_id, client_secret)
		token = Token(access_token) if access_token else None
		self._init(HTTPClient(cc, grant, token))

	def _init(self, http):
		self.http = http

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

	def request(self, verb, path, *, params=None, data=None, headers=None, timeout=8):
		return self.http.request(verb, path, params=params, data=data, headers=headers, timeout=timeout)

	def request_json(self, *args, **kwargs):
		resp = self.request(*args, **kwargs)
		return response_json(resp)

	def close(self):
		self.http.close()

ClientCore = Client


class Client(ClientCore):
	def _init(self, http):
		super()._init(http)
		self.api = ...
