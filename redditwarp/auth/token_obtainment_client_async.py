
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
	from .client_credentials import ClientCredentials
	from .grants import AuthorizationGrant
	from ..http.requestor_async import Requestor

from .. import http
from ..http.request import Request
from ..http.misc import json_loads_response
from ..http.payload import FormData
from .token import ResponseToken
from .util import apply_basic_auth
from .exceptions import (
	ResponseException,
	ResponseContentError,
	HTTPStatusError,
	oauth2_response_error_class_by_error_name,
)

__all__ = ('TokenObtainmentClient',)

class TokenObtainmentClient:
	def __init__(self, requestor: Requestor, uri: str,
			client_credentials: ClientCredentials, grant: AuthorizationGrant) -> None:
		self.requestor = requestor
		self.uri = uri
		self.client_credentials = client_credentials
		self.grant = grant

	async def fetch_json_dict(self) -> Mapping[str, Any]:
		data = {k: v for k, v in vars(self.grant).items() if v}
		data['grant_type'] = self.grant.GRANT_TYPE

		r = Request('POST', self.uri, payload=FormData(data))
		apply_basic_auth(r, self.client_credentials)

		resp = await self.requestor.request(r)

		try:
			resp_json = json_loads_response(resp)
		except ValueError:
			raise ResponseContentError(response=resp) from None

		error = resp_json.get('error')
		if error:
			clss = oauth2_response_error_class_by_error_name.get(error)
			if clss:
				raise clss.from_response_and_json(resp, resp_json)

		try:
			resp.raise_for_status()
		except http.exceptions.StatusCodeException as e:
			raise HTTPStatusError(response=resp) from e

		if error:
			raise ResponseException(response=resp)

		return resp_json

	async def fetch_token(self) -> ResponseToken:
		return ResponseToken.from_dict(await self.fetch_json_dict())
