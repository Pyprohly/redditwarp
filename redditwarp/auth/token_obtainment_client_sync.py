
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, Any
if TYPE_CHECKING:
	from .client_credentials import ClientCredentials
	from .grants import AuthorizationGrant
	from ..http.requestor_sync import Requestor

from .. import http
from ..http.request import Request
from ..http.misc import json_loads_response
from ..http.payload import FormData
from .token import ResponseToken
from .util import apply_basic_auth
from .exceptions import (
	ResponseContentError,
	UnrecognizedOAuth2ResponseError,
	HTTPStatusError,
	oauth2_response_error_class_by_error_name,
)

__all__ = ('TokenObtainmentClient',)

class TokenObtainmentClient:
	"""The token client will exchange an authorisation grant
	for an OAuth2 token.
	"""

	def __init__(self, requestor: Requestor, uri: str,
			client_credentials: ClientCredentials,
			grant: Optional[AuthorizationGrant] = None,
			grant_info: Optional[Mapping[str, str]] = None) -> None:
		self.requestor = requestor
		self.uri = uri
		self.client_credentials = client_credentials

		if grant_info is None:
			if grant is None:
				raise TypeError
			grant_info = vars(grant)
		self.grant_info: Mapping[str, str] = grant_info

	def set_grant(self, grant: AuthorizationGrant) -> None:
		self.grant_info = vars(grant)

	def fetch_json_dict(self) -> Mapping[str, Any]:
		data = dict(self.grant_info)
		r = Request('POST', self.uri, payload=FormData(data))
		apply_basic_auth(r, self.client_credentials)

		resp = self.requestor.request(r)

		try:
			resp_json = json_loads_response(resp)
		except ValueError:
			raise ResponseContentError(response=resp) from None

		error = resp_json.get('error')
		if error:
			clss = oauth2_response_error_class_by_error_name.get(error)
			if clss is not None:
				raise clss.from_json_dict(resp, resp_json)

		try:
			resp.raise_for_status()
		except http.exceptions.StatusCodeException as e:
			raise HTTPStatusError(response=resp) from e

		if error:
			raise UnrecognizedOAuth2ResponseError(response=resp)

		return resp_json

	def fetch_token(self) -> ResponseToken:
		return ResponseToken.from_dict(self.fetch_json_dict())
