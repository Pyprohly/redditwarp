
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .grant import AuthorizationGrant
	from ..requestor import Requestor

from dataclasses import dataclass
from base64 import b64encode

from ..http.request import Request
from ..http.util import response_json
from .token import TokenResponse
from .exceptions import (
	AuthResponseError,
	Unauthorized,
	oauth_error_response_classes,
)

__all__ = (
	'ClientCredentials',
	'TokenClient',
	'apply_basic_auth',
)

@dataclass
class ClientCredentials:
	client_id: str
	client_secret: str

class TokenClient:
	"""The token client will exchange an authorisation grant
	for an OAuth2 token.
	"""

	def __init__(self, requestor: Requestor, token_endpoint: str,
			client_credentials: ClientCredentials, grant: AuthorizationGrant):
		self.requestor = requestor
		self.token_endpoint = token_endpoint
		self.client_credentials = client_credentials
		self.grant = grant

	def fetch_token(self) -> TokenResponse:
		params = {k: v for k, v in vars(self.grant).items() if v}
		params['grant_type'] = self.grant.grant_type

		r = Request('POST', self.token_endpoint, params=params)
		apply_basic_auth(self.client_credentials, r)

		resp = self.requestor.request(r)
		resp_json = response_json(resp)

		error = resp_json.get('error')
		if error:
			if 400 <= resp.status < 500:
				if error == 401:
					raise Unauthorized(resp)

				assert False
				raise AuthResponseError(resp)

			try:
				cls = oauth_error_response_classes[error]
			except KeyError:
				assert False
				raise AuthResponseError(resp)
			raise cls.from_response_and_json(resp, resp_json)

		return TokenResponse(**resp_json)

def apply_basic_auth(client_credentials: ClientCredentials, request: Request) -> None:
	ci = client_credentials.client_id
	cs = client_credentials.client_secret
	auth_string = b'basic ' + b64encode(f'{ci}:{cs}'.encode())
	request.headers['Authorization'] = auth_string
