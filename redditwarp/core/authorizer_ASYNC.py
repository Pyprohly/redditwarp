
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
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
from ..auth.grants import RefreshTokenGrant
from ..auth.exceptions import (
    UnknownTokenType,
    extract_www_authenticate_auth_params,
    raise_for_resource_server_response_error,
)

class Authorizer:
    def __init__(self,
        token_client: Optional[TokenObtainmentClient] = None,
        token: Optional[Token] = None,
    ):
        self.token_client = token_client
        self.token = token
        self.renewal_time: Optional[int] = None
        self.renewal_skew: int = 30
        self.expires_in_fallback: Optional[int] = None
        self.time_func: Callable[[], float] = time.monotonic

    def current_time(self) -> float:
        return self.time_func()

    async def renew_token(self) -> None:
        if self.token_client is None:
            raise RuntimeError('no token client')

        self.token = tk = await self.token_client.fetch_token()

        if tk.token_type.lower() != 'bearer':
            raise UnknownTokenType(token=tk)

        if tk.refresh_token:
            self.token_client.grant = RefreshTokenGrant(tk.refresh_token)

        expires_in: Optional[int] = tk.expires_in
        if expires_in is None:
            expires_in = self.expires_in_fallback
        if expires_in is None:
            self.renewal_time = None
        else:
            self.renewal_time = int(self.current_time()) + expires_in - self.renewal_skew

    def should_renew_token(self) -> bool:
        if self.token is None:
            return True
        if self.renewal_time is None:
            return False
        return self.current_time() >= self.renewal_time

    def can_renew_token(self) -> bool:
        return self.token_client is not None

    def prepare_request(self, request: Request) -> None:
        tk = self.token
        if tk is None:
            raise RuntimeError('no token is set')
        request.headers['Authorization'] = f'{tk.token_type} {tk.access_token}'


class Authorized(RequestorDecorator):
    def __init__(self, requestor: Requestor, authorizer: Authorizer) -> None:
        super().__init__(requestor)
        self.authorizer = authorizer
        self._lock = asyncio.Lock()
        self._valve = asyncio.Event()
        self._valve.set()
        self._futures: set[asyncio.Future[Response]] = {*()}

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        await self._valve.wait()

        authorizer = self.authorizer
        async with self._lock:
            if authorizer.should_renew_token():
                await authorizer.renew_token()
        authorizer.prepare_request(request)

        coro = self.requestor.send(request, timeout=timeout)
        task = asyncio.create_task(coro)
        self._futures.add(task)
        try:
            resp = await task
        finally:
            self._futures.remove(task)

        auth_params = extract_www_authenticate_auth_params(resp)
        invalid_token = auth_params.get('error', '') == 'invalid_token'

        if invalid_token and authorizer.can_renew_token():
            # Need to call `renew_token()` ensuring only one task does it.
            if self._valve.is_set():
                # Suspend making new requests, as they would fail on the old token.
                self._valve.clear()

                await authorizer.renew_token()

                # Wait for the remaining requests to finish to ensure that
                # a request that fails on the same old token doesn't cause
                # another token renewal.
                if x := self._futures:
                    await asyncio.wait(x)

                # Resume making requests.
                self._valve.set()
            else:
                await self._valve.wait()

            authorizer.prepare_request(request)

            resp = await self.requestor.send(request, timeout=timeout)

            auth_params = extract_www_authenticate_auth_params(resp)

        raise_for_resource_server_response_error(auth_params)

        return resp
