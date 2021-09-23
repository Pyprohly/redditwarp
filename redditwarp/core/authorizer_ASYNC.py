
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Set, Callable
if TYPE_CHECKING:
    from ..auth.token_obtainment_client_ASYNC import TokenObtainmentClient
    from ..auth.token import Token
    from ..http.requestor_ASYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

from ..util.imports import lazy_import
if TYPE_CHECKING:
    import asyncio
else:
    lazy_import % 'asyncio'

import time

from ..http.requestor_decorator_ASYNC import RequestorDecorator
from .exceptions import UnknownTokenType
from ..auth.grants import RefreshTokenGrant
from ..auth.exceptions import extract_www_authenticate_bearer_auth_params, raise_for_resource_server_response_error

class Authorizer:
    def __init__(self,
        token_client: Optional[TokenObtainmentClient] = None,
        token: Optional[Token] = None,
    ):
        self.token_client = token_client
        self.token = token
        self.expiry_skew = 30
        self.expiry_time: Optional[int] = None
        self.expires_in_fallback: Optional[int] = None
        self.honor_refresh_token = True
        self.time_func: Callable[[], float] = time.monotonic
        self._lock = asyncio.Lock()

    def token_expired(self) -> bool:
        if self.expiry_time is None:
            return False
        return self.current_time() > self.expiry_time

    def can_renew_token(self) -> bool:
        return self.token_client is not None

    async def renew_token(self) -> None:
        if self.token_client is None:
            raise RuntimeError('no token client')

        self.token = tk = await self.token_client.fetch_token()

        if tk.token_type.lower() != 'bearer':
            raise UnknownTokenType(token=tk)

        if self.honor_refresh_token:
            if tk.refresh_token:
                self.token_client.grant = RefreshTokenGrant(tk.refresh_token)

        if tk.expires_in is None:
            if self.expires_in_fallback is None:
                self.expiry_time = None
            else:
                self.expiry_time = int(self.current_time()) + self.expires_in_fallback - self.expiry_skew
        else:
            self.expiry_time = int(self.current_time()) + tk.expires_in - self.expiry_skew

    async def maybe_renew_token(self) -> None:
        async with self._lock:
            if (self.token is None) or self.token_expired():
                await self.renew_token()

    def prepare_request(self, request: Request) -> None:
        tk = self.token
        if tk is None:
            raise RuntimeError('no token is set')
        request.headers['Authorization'] = f'{tk.token_type} {tk.access_token}'

    def current_time(self) -> float:
        return self.time_func()

    def remaining_time(self) -> Optional[float]:
        if self.expiry_time is None:
            return None
        return self.expiry_time - self.current_time()


class Authorized(RequestorDecorator):
    def __init__(self, requestor: Requestor, authorizer: Authorizer) -> None:
        super().__init__(requestor)
        self.authorizer = authorizer
        self._valve = asyncio.Event()
        self._valve.set()
        self._futures: Set[asyncio.Future[Response]] = set()

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        await self._valve.wait()

        await self.authorizer.maybe_renew_token()
        self.authorizer.prepare_request(request)

        coro = self.requestor.send(request, timeout=timeout)
        fut = asyncio.ensure_future(coro)
        self._futures.add(fut)
        try:
            resp = await fut
        finally:
            self._futures.remove(fut)

        auth_params = extract_www_authenticate_bearer_auth_params(resp)
        invalid_token = auth_params.get('error', '') == 'invalid_token'

        if invalid_token and self.authorizer.can_renew_token():
            # Need to call `renew_token()` ensuring only one task does it.
            if self._valve.is_set():
                # Stop new requests. Assume the token we have is invalid.
                self._valve.clear()

                await self.authorizer.renew_token()

                # Wait for all other requests to finish so that
                # a request that fails on the same old token
                # doesn't cause another token renewal.
                if self._futures:
                    await asyncio.wait(self._futures)

                self._valve.set()
            else:
                await self._valve.wait()

            self.authorizer.prepare_request(request)

            resp = await self.requestor.send(request, timeout=timeout)

            auth_params = extract_www_authenticate_bearer_auth_params(resp)

        raise_for_resource_server_response_error(resp, auth_params)

        return resp
