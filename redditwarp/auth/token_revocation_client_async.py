
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .client_credentials import ClientCredentials
	from ..http.requestor_async import Requestor

from .. import http
from ..http.request import Request
from ..http.payload import FormData
from .util import apply_basic_auth
from .exceptions import HTTPStatusError

__all__ = ('TokenRevocationClient',)

class TokenRevocationClient:
	def __init__(self, requestor: Requestor, endpoint: str,
			client_credentials: ClientCredentials) -> None:
		self.requestor = requestor
		self.endpoint = endpoint
		self.client_credentials = client_credentials

	async def revoke_token(self, token: str, token_type_hint: Optional[str] = None) -> None:
		data = {'token': token}
		if token_type_hint:
			data['token_type_hint'] = token_type_hint

		r = Request('POST', self.endpoint, payload=FormData(data))
		apply_basic_auth(r, self.client_credentials)

		resp = await self.requestor.request(r)

		try:
			resp.raise_for_status()
		except http.exceptions.StatusCodeException as e:
			raise HTTPStatusError(resp) from e

	async def revoke_access_token(self, token: str) -> None:
		await self.revoke_token(token, 'access_token')

	async def revoke_refresh_token(self, token: str) -> None:
		await self.revoke_token(token, 'refresh_token')
