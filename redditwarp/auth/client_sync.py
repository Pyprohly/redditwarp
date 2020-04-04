
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .grants import AuthorizationGrant
	from ..http.requestor import Requestor

from ..http.request import Request
from ..http.util import json_loads_response
from .token import TokenResponse
from .exceptions import (
	AuthResponseError,
	Unauthorized,
	oauth2_response_error_class_by_error_name,
)

__all__ = ('TokenClient',)

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
		params['grant_type'] = self.grant.GRANT_TYPE

		r = Request('POST', self.token_endpoint, params=params)
		apply_basic_auth(self.client_credentials, r)

		resp = self.requestor.request(r)
		resp_json = json_loads_response(resp)

		error = resp_json.get('error')
		if error:
			if 400 <= resp.status < 500:
				if error == 401:
					raise Unauthorized(resp)
				assert False
				raise AuthResponseError(resp)

			try:
				clss = oauth2_response_error_class_by_error_name[error]
			except KeyError:
				assert False
				raise AuthResponseError(resp)
			raise clss.from_response_and_json(resp, resp_json)

		return TokenResponse(**resp_json)


from .client import ClientCredentials, apply_basic_auth
