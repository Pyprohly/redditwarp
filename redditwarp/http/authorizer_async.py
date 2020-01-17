
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from ..auth.client_async import TokenClient
	from .requestor_async import Requestor
	from .request import Request
	from .response import Response
	from .token import TokenResponse

import asyncio
import time

from .requestor_async import RequestorDecorator
from ..auth import Token

class Authorizer:
	def __init__(self, token_client: TokenClient, token: Optional[Token] = None, expiry_skew: int = 30) -> None:
		self.token_client = token_client
		self.token = token
		self.expiry_skew = expiry_skew
		self.expiry_time = 0
		self.expires_in_fallback = 3600

	def token_expired(self) -> bool:
		return self.current_time() > self.expiry_time

	async def renew_token(self) -> Token:
		tr: TokenResponse = await self.token_client.fetch_token()
		expires_in = tr.expires_in
		if expires_in is None:
			expires_in = self.expires_in_fallback

		self.expiry_time = int(self.current_time()) + expires_in - self.expiry_skew
		self.token = token = Token(
			access_token=tr.access_token,
			refresh_token=tr.refresh_token,
			expires_in=expires_in,
			scope=tr.scope,
		)
		return token

	async def prepare(self):
		if (self.token is None) or self.token_expired():
			await self.renew_token()

	def prepare_request(self, request: Request) -> None:
		request.headers['Authorization'] = '{0.token_type} {0.access_token}'.format(self.token)

	def current_time(self):
		return time.monotonic()

	def remaining_time(self) -> int:
		return self.expiry_time - int(self.current_time())


class Authorized(RequestorDecorator):
	def __init__(self, requestor: Requestor, authorizer: Optional[Authorizer] = None) -> None:
		super().__init__(requestor)
		self.authorizer = authorizer
		self._lock = asyncio.Lock()
		self._event = asyncio.Event()
		self._event.set()
		self._futures = []

	async def request(self, request: Request, timeout: Optional[int]) -> Response:
		await self._event.wait()

		async with self._lock:
			await self.prepare_request(request)

		fut = asyncio.ensure_future(
				self.requestor.request(request, timeout))
		self._futures.append(fut)
		response = await fut

		# Find and remove any completed task instead of just doing
		# `self._futures.remove(fut)` so cancelled requests don't
		# leave objects stuck in `self._futures` forever.
		for f in self._futures:
			if f.done():
				self._futures.remove(f)

		if response.status == 401:
			if self._event.is_set():
				# Stop new requests being made.
				self._event.clear()

				# Ensure all tasks are past the 401 check on
				# `self._event.wait()` so `renew_token()` isn't called twice.
				await asyncio.wait(self._futures)

				await self.authorizer.renew_token()
				self._event.set()
			else:
				await self._event.wait()

			response = await self.requestor.request(request, timeout)

		return response

	async def prepare_request(self, request: Request) -> None:
		if 'Authorization' not in request.headers:
			await self.authorizer.prepare()
			self.authorizer.prepare_request(request)
