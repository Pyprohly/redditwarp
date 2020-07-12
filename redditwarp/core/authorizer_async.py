
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, List
if TYPE_CHECKING:
    from ..auth.token_obtainment_client_async import TokenObtainmentClient
    from ..auth.token import Token
    from ..http.requestor_async import Requestor
    from ..http.request import Request
    from ..http.response import Response

import asyncio
import time

from ..http.requestor_async import RequestorDecorator
from .exceptions import UnknownTokenType

class Authorizer:
    def __init__(self,
        token: Optional[Token],
        token_client: Optional[TokenObtainmentClient],
    ) -> None:
        self.token = token
        self.token_client = token_client
        self.expiry_skew = 30
        self.expiry_time: Optional[int] = None
        self.expires_in_fallback: Optional[int] = None

    def token_expired(self) -> bool:
        if self.expiry_time is None:
            return False
        return self.current_time() > self.expiry_time

    def can_renew_token(self) -> bool:
        return self.token_client is not None

    async def renew_token(self) -> None:
        if self.token_client is None:
            raise RuntimeError('a new token was requested but no token client is assigned')

        self.token = tk = await self.token_client.fetch_token()

        if tk.token_type.lower() != 'bearer':
            raise UnknownTokenType(token=tk)

        if tk.expires_in is None:
            if self.expires_in_fallback is None:
                self.expiry_time = None
            else:
                self.expiry_time = int(self.current_time()) + self.expires_in_fallback - self.expiry_skew
        else:
            self.expiry_time = int(self.current_time()) + tk.expires_in - self.expiry_skew

    async def maybe_renew_token(self) -> None:
        if (self.token is None) or self.token_expired():
            await self.renew_token()

    def prepare_request(self, request: Request) -> None:
        tk = self.token
        if tk is None:
            raise RuntimeError('no token is set')
        request.headers['Authorization'] = f'{tk.token_type} {tk.access_token}'

    def current_time(self) -> float:
        return time.monotonic()

    def remaining_time(self) -> Optional[float]:
        if self.expiry_time is None:
            return None
        return self.expiry_time - self.current_time()


class Authorized(RequestorDecorator):
    def __init__(self, requestor: Requestor, authorizer: Authorizer) -> None:
        super().__init__(requestor)
        self.authorizer = authorizer
        self._lock = asyncio.Lock()
        self._valve = asyncio.Event()
        self._valve.set()
        self._futures: List[asyncio.Future] = []

    async def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping] = None) -> Response:
        await self._valve.wait()

        async with self._lock:
            await self.authorizer.maybe_renew_token()
        self.authorizer.prepare_request(request)

        coro = self.requestor.send(request, timeout=timeout, aux_info=aux_info)
        fut = asyncio.ensure_future(coro)
        self._futures.append(fut)
        try:
            response = await fut
        finally:
            self._futures.remove(fut)

        if response.status == 401 and self.authorizer.can_renew_token():
            # Need to call `renew_token()`.
            # Ensure only one task does it
            if self._valve.is_set():
                # Stop new requests from being made
                self._valve.clear()

                # Ensure all tasks are past the 401 response status check
                # and are awaiting on `self._valve.wait()`
                await asyncio.wait(self._futures)

                await self.authorizer.renew_token()
                self.authorizer.prepare_request(request)

                self._valve.set()
            else:
                await self._valve.wait()

            response = await self.requestor.send(request, timeout=timeout, aux_info=aux_info)

        return response
