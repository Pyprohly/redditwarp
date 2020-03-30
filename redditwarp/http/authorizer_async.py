
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
	from ..auth.client_async import TokenClient
	from ..auth.token import TokenResponse
	from .requestor_async import Requestor
	from .request import Request
	from .response import Response

import asyncio
import time

from .requestor_async import RequestorDecorator
from ..auth import Token

class Authorizer:
	def __init__(self, token: Optional[Token] = None,
			token_client: Optional[TokenClient] = None,
			expiry_skew: int = 30) -> None:
		self.token = token
		self.token_client = token_client
		self.expiry_skew = expiry_skew
		self.expiry_time: Optional[int] = None
		self.expires_in_fallback: int = 3600

	def token_expired(self) -> bool:
		if self.expiry_time is None:
			return False
		return self.current_time() > self.expiry_time

	def can_renew_token(self) -> bool:
		return self.token_client is not None

	async def renew_token(self) -> Token:
		if self.token_client is None:
			raise RuntimeError('a new token was requested but no token client is set')

		tr: TokenResponse = await self.token_client.fetch_token()

		expires_in = tr.expires_in
		if expires_in is None:
			expires_in = self.expires_in_fallback

		self.expiry_time = int(self.current_time()) + expires_in - self.expiry_skew
		token = Token(
			access_token=tr.access_token,
			refresh_token=tr.refresh_token,
			expires_in=expires_in,
			scope=tr.scope,
		)
		self.token = token
		return token

	async def maybe_renew_token(self) -> Optional[Token]:
		if (self.token is None) or self.token_expired():
			return await self.renew_token()
		return None

	def prepare_request(self, request: Request) -> None:
		if self.token is None:
			raise RuntimeError('no token is set')
		request.headers['Authorization'] = '{0.TOKEN_TYPE} {0.access_token}'.format(self.token)

	def current_time(self) -> float:
		return time.monotonic()

	def remaining_time(self) -> Optional[int]:
		if self.expiry_time is None:
			return None
		return self.expiry_time - int(self.current_time())


class Authorized(RequestorDecorator):
	def __init__(self, requestor: Requestor, authorizer: Authorizer) -> None:
		super().__init__(requestor)
		self.authorizer = authorizer
		self._lock = asyncio.Lock()
		self._valve = asyncio.Event()
		self._valve.set()
		self._futures: List[asyncio.Future] = []

	async def request(self, request: Request, timeout: Optional[int] = None) -> Response:
		await self._valve.wait()

		async with self._lock:
			await self.authorizer.maybe_renew_token()
			self.authorizer.prepare_request(request)

		fut = asyncio.ensure_future(self.requestor.request(request, timeout))
		self._futures.append(fut)
		response = await fut

		# Find and remove any completed task instead of just doing
		# `self._futures.remove(fut)` so that cancelled requests
		# don't leave objects stuck in `self._futures` forever.
		for f in self._futures.copy():
			if f.done():
				self._futures.remove(f)

		if response.status == 401 and self.authorizer.can_renew_token():
			# We need to call `renew_token()` but ensure only one task does it.
			if self._valve.is_set():
				# Stop new requests from being made.
				self._valve.clear()

				# Ensure all tasks are past the 401 status check and awaiting on
				# `self._valve.wait()`.
				await asyncio.wait(self._futures)

				await self.authorizer.renew_token()
				self.authorizer.prepare_request(request)

				self._valve.set()
			else:
				await self._valve.wait()

			response = await self.requestor.request(request, timeout)

		return response
