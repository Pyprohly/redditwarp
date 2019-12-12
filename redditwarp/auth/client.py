
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .provider import Provider
	from .credentials import ClientCredentials
	from .grant import AuthorizationGrant
	from ..requestor import Requestor

from base64 import b64encode

from .token import TokenResponse
from ..request import Request
from ..util import response_json


class TokenClient:
	"""The token client will exchange an authorisation grant
	for an OAuth2 token.
	"""

	def __init__(self, requestor: Requestor, provider: Provider,
			client_credentials: ClientCredentials, grant: AuthorizationGrant):
		self.requestor = requestor
		self.provider = provider
		self.client_credentials = client_credentials
		self.grant = grant

	def fetch_token(self) -> TokenResponse:
		params = {k: v for k, v in vars(self.grant).items() if v}
		params['grant_type'] = self.grant.grant_type

		r = Request('POST', self.provider.token_endpoint, params=params)
		apply_basic_auth(self.client_credentials, r)

		resp = self.requestor.request(r)
		json_dict = response_json(resp)
		import builtins; builtins.resp = resp
		return TokenResponse(**json_dict)

def apply_basic_auth(client_credentials: ClientCredentials, request: Request) -> None:
	ci = client_credentials.client_id
	cs = client_credentials.client_secret
	auth_string = b'basic ' + b64encode(f'{ci}:{cs}'.encode())
	request.headers['Authorization'] = auth_string
