
from base64 import b64encode

from .token import TokenResponse
from ..transport import Request


class TokenClient:
	"""The token client will exchange an authorisation grant
	for an OAuth2 token.
	"""

	@property
	def grant(self) -> AuthorizationGrant:
		return self._grant

	def __init__(self, requestor: Requestor, provider: Provider,
			client_credentials: ClientCredentials, grant: AuthorizationGrant):
		self.requestor = requestor
		self.provider = provider
		self.client_credentials = client_credentials
		self._grant = grant

	def fetch_token() -> TokenResponse:
		raise NotImplementedError

class AuthorizationCodeClient(TokenClient):
	grant: AuthorizationCodeGrant

	def fetch_token() -> TokenResponse:
		...

class ResourceOwnerPasswordCredentialsClient(TokenClient):
	grant: ResourceOwnerPasswordCredentialsGrant

	def fetch_token() -> TokenResponse:
		...

class ClientCredentialsClient(TokenClient):
	grant: ClientCredentialsGrant

	def fetch_token() -> TokenResponse:
		r = Request('POST', self.provider.token_endpoint, headers=headers)
		apply_client_credentials_basic_auth(r, self.client_credentials)
		resp = self.requestor.request(r)
		json_dict = json_from_response(resp)
		return TokenResponse(json_dict)

class RefreshTokenClient(TokenClient):
	grant: RefreshTokenGrant

	def fetch_token() -> TokenResponse:
		...


def apply_client_credentials_basic_auth(request: Request, client_credentials: ClientCredentials) -> None:
	client_id = client_credentials.client_id
	client_secret = client_credentials.client_secret
	auth_string = 'basic ' + b64encode(f'{client_id}:{client_secret}'.encode()).decode()
	request.headers['Authorization'] = auth_string
