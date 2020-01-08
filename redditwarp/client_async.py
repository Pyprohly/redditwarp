
from .http.client_async import HTTPClient

from .auth import (
	ClientCredentials,
	Token,
	auto_grant_factory,
)

from .http.util import response_json


class Client:
	@classmethod
	def from_http(cls, http):
		self = cls.__new__(cls)
		self._init(http)
		return self

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
		else:
			if any(auto_grant_creds):
				raise TypeError("you shouldn't pass grant credentials if you explicitly provide a grant")

		cc = ClientCredentials(client_id, client_secret)
		token = Token(access_token) if access_token else None
		self._init(HTTPClient(cc, grant, token))

	def _init(self, http):
		self.http = http

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc_value, traceback):
		await self.close()

	async def request(self, verb, path, *, params=None, data=None, headers=None):
		return await self.http.request(verb, path, params=params, data=data, headers=headers)

	async def request_json(self, *args, **kwargs):
		resp = await self.request(*args, **kwargs)
		return response_json(resp)

	async def close(self):
		await self.http.close()
