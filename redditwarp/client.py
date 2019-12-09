
from .http import HTTPClient
from .http.client import DEFAULT_PROVIDER as _DEFAULT_PROVIDER
from .http.auth.grant import auto_grant_factory

class Client:
	def __init__(self, client_id, client_secret, refresh_token=None, *,
			access_token=None, username=None, password=None):
		grant = auto_grant_factory(
			client_id=client_id,
			client_secret=client_secret,
			refresh_token=refresh_token,
			username=username,
			password=password,
		)
		if grant is None:
			raise TypeError('An authorization grant could not be made from the provided credentials.')

		client_credentials = ClientCredentials(client_id, client_secret)
		token_client = TokenClient(Session(), _DEFAULT_PROVIDER, client_credentials, grant)
		token = Token(access_token) if access_token else None
		authorizer = Authorizer(token_client, token)
		self._init(authorizer)

	def _init(self, authorizer):
		self.http = HTTPClient(Session(), authorizer)

	@classmethod
	def from_authorizer(cls, authorizer):
		return cls._init(authorizer)

	def __class_getitem__(cls, authorizer):
		return cls.from_authorizer(authorizer)

	def request(self, verb, path, *, params=None, data=None, headers=None):
		return self.http.request(verb, path, params=params, data=data, headers=headers)
