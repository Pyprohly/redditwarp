
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .provider import Provider
	from .credentials import ClientCredentials
	from .grant import AuthorizationGrant
	from ..requestor import Requestor

from base64 import b64encode
from dataclasses import asdict

from .token import TokenResponse
from ..request import Request
from ..util import response_json


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

	def fetch_token(self) -> TokenResponse:
		params = {k: v for k, v in asdict(self.grant).items() if v}
		r = Request('POST', self.provider.token_endpoint, params=params)
		apply_basic_auth(self.client_credentials, r)
		resp = self.requestor.request(r)
		json_dict = response_json(resp)
		return TokenResponse(**json_dict)


class AuthorizationCodeClient(TokenClient):
	grant: AuthorizationCodeGrant

class ResourceOwnerPasswordCredentialsClient(TokenClient):
	grant: ResourceOwnerPasswordCredentialsGrant

class ClientCredentialsClient(TokenClient):
	grant: ClientCredentialsGrant

class RefreshTokenClient(TokenClient):
	grant: RefreshTokenGrant


def apply_basic_auth(client_credentials: ClientCredentials, request: Request) -> None:
	ci = client_credentials.client_id
	cs = client_credentials.client_secret
	auth_string = 'basic ' + b64encode(f'{ci}:{cs}'.encode()).decode()
	request.headers['Authorization'] = auth_string
