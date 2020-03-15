
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
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
	def __init__(self, token_client: TokenClient, token: Optional[Token] = None, expiry_skew: int = 30) -> None:
		self.token_client = token_client
		self.token = token
		self.expiry_skew = expiry_skew
		self.expiry_time: Optional[int] = None
		self.expires_in_fallback: int = 3600

	def token_expired(self) -> bool:
		if self.expiry_time is None:
			return False
		return self.current_time() > self.expiry_time

	async def renew_token(self) -> Token:
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

	async def maybe_renew_token(self) -> None:
		if (self.token is None) or self.token_expired():
			await self.renew_token()

	def prepare_request(self, request: Request) -> None:
		request.headers['Authorization'] = '{0.token_type} {0.access_token}'.format(self.token)

	def current_time(self) -> float:
		return time.monotonic()

	def remaining_time(self) -> Optional[int]:
		if self.expiry_time is None:
			return None
		return self.expiry_time - int(self.current_time())


class Authorized(RequestorDecorator):
	def __init__(self, requestor: Requestor, authorizer: Optional[Authorizer] = None) -> None:
		super().__init__(requestor)
		self.authorizer = authorizer
		self._lock = asyncio.Lock()
		self._valve = asyncio.Event()
		self._valve.set()
		self._futures = []

	async def prepare_request(self, request: Request) -> None:
		if 'Authorization' not in request.headers:
			await self.authorizer.maybe_renew_token()
			self.authorizer.prepare_request(request)

	async def request(self, request: Request, timeout: Optional[int]) -> Response:
		await self._valve.wait()

		async with self._lock:
			await self.prepare_request(request)

		fut = asyncio.ensure_future(self.requestor.request(request, timeout))
		self._futures.append(fut)
		response = await fut

		# Find and remove any completed task instead of just doing
		# `self._futures.remove(fut)` so that cancelled requests
		# don't leave objects stuck in `self._futures` forever.
		for f in self._futures.copy():
			if f.done():
				self._futures.remove(f)

		if response.status == 401:
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
