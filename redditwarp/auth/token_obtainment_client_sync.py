
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .client_credentials import ClientCredentials
	from .grants import AuthorizationGrant
	from ..http.requestor_sync import Requestor

from ..http.request import Request
from ..http.util import json_loads_response
from ..http.payload import FormData
from .token import TokenResponse
from .misc import apply_basic_auth
from .exceptions import (
	AuthResponseException,
	Unauthorized,
	oauth2_response_error_class_by_error_name,
	get_response_content_error,
)

__all__ = ('TokenObtainmentClient',)

class TokenObtainmentClient:
	"""The token client will exchange an authorisation grant
	for an OAuth2 token.
	"""

	def __init__(self, requestor: Requestor, endpoint: str,
			client_credentials: ClientCredentials, grant: AuthorizationGrant) -> None:
		self.requestor = requestor
		self.endpoint = endpoint
		self.client_credentials = client_credentials
		self.grant = grant

	def fetch_token(self) -> TokenResponse:
		data = {k: v for k, v in vars(self.grant).items() if v}
		data['grant_type'] = self.grant.GRANT_TYPE

		r = Request('POST', self.endpoint, payload=FormData(data))
		apply_basic_auth(r, self.client_credentials)

		resp = self.requestor.request(r)

		try:
			resp_json = json_loads_response(resp)
		except ValueError:
			raise get_response_content_error(resp) from None

		error = resp_json.get('error')
		if error:
			if error == 401:
				raise Unauthorized(resp)

			try:
				clss = oauth2_response_error_class_by_error_name[error]
			except KeyError:
				raise AuthResponseException(resp) from None
			raise clss.from_response_and_json(resp, resp_json)

		return TokenResponse.from_kwargs(**resp_json)
