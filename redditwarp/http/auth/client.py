
from base64 import b64encode

from .token import TokenResponse
from ..transport import Request


T = TypeVar('T', bound=AuthorizationGrant)

class TokenClient(Generic[T]):
	"""The token client will exchange an authorisation grant
	for an OAuth2 token.
	"""
	def __init__(self, requestor, provider, client_credentials, grant: T):
		self.requestor = requestor
		self.provider = provider
		self.client_credentials = client_credentials
		self.grant = grant

	def retrieve_token() -> TokenResponse:
		raise NotImplementedError

class AuthorizationCodeClient(TokenClient):
	def retrieve_token():
		...

class ImplicitClient(TokenClient):
	def retrieve_token():
		...

class ResourceOwnerPasswordCredentialsClient(TokenClient):
	def retrieve_token():
		...

class ClientCredentialsClient(TokenClient[ClientCredentialsGrant]):
	def retrieve_token() -> TokenResponse:
		headers = basic_auth_header(self.client_credentials)
		r = Request('POST', self.provider.token_endpoint, headers=headers)
		resp = self.requestor.request(r)
		resp = 


def basic_auth_header(client_credentials):
	client_id = client_credentials.client_id
	client_secret = client_credentials.client_secret
	basic_auth = 'basic ' + b64encode(f'{client_id}:{client_secret}'.encode()).decode()
	return {'Authorization': basic_auth}
