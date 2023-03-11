
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable, MutableMapping
if TYPE_CHECKING:
    from ..auth.token_obtainment_client_ASYNC import TokenObtainmentClient
    from ..auth.token import Token
    from ...http.handler_ASYNC import Handler
    from ...http.requisition import Requisition
    from ...http.send_params import SendParams
    from ...http.exchange import Exchange

from ...util.imports import lazy_import
if TYPE_CHECKING:
    import asyncio
else:
    lazy_import % 'asyncio'

import time

from ...http.delegating_handler_ASYNC import DelegatingHandler


class Authorizer:
    def __init__(self,
        token_client: Optional[TokenObtainmentClient] = None,
        token: Optional[Token] = None,
    ) -> None:
        self._token_client: Optional[TokenObtainmentClient] = token_client
        ("")
        self._token: Optional[Token] = token
        ("")
        self.renewal_time: Optional[float] = None
        ("")
        self.renewal_skew: float = 30
        ("")
        self.expires_in_fallback: Optional[int] = None
        ("")
        self.time_func: Callable[[], float] = time.monotonic
        ("")
        self.authorization_header_name: str = 'Authorization'
        ("")

    def has_token_client(self) -> bool:
        return self._token_client is not None

    def fetch_token_client(self) -> TokenObtainmentClient:
        v = self._token_client
        if v is None:
            raise RuntimeError('token client not set')
        return v

    def set_token_client(self, value: Optional[TokenObtainmentClient]) -> None:
        self._token_client = value

    def has_token(self) -> bool:
        return self._token is not None

    def fetch_token(self) -> Token:
        v = self._token
        if v is None:
            raise RuntimeError('token not set')
        return v

    def set_token(self, value: Optional[Token]) -> None:
        self._token = value

    async def renew_token(self) -> None:
        tc = self.fetch_token_client()
        tk = await tc.fetch_token()

        self.set_token(tk)

        expires_in = tk.expires_in
        if expires_in is None:
            expires_in = self.expires_in_fallback
        if expires_in is None:
            self.renewal_time = None
        else:
            self.renewal_time = self.time() + expires_in - self.renewal_skew

    def time(self) -> float:
        return self.time_func()

    def should_renew_token(self) -> bool:
        if not self.has_token():
            return True
        if self.renewal_time is None:
            return False
        return self.time() >= self.renewal_time

    def can_renew_token(self) -> bool:
        return self.has_token_client()

    async def attain_token(self) -> Token:
        if self.should_renew_token():
            await self.renew_token()
        return self.fetch_token()

    def get_header_entry(self) -> tuple[str, str]:
        return (self.authorization_header_name, 'Bearer {0.access_token}'.format(self.fetch_token()))

    def prepare_requisition(self, requisition: Requisition) -> None:
        self.prepare_headers(requisition.headers)

    def prepare_headers(self, headers: MutableMapping[str, str]) -> None:
        k, v = self.get_header_entry()
        headers[k] = v


class Authorized(DelegatingHandler):
    def __init__(self, handler: Handler, authorizer: Authorizer) -> None:
        super().__init__(handler)
        self.authorizer: Authorizer = authorizer
        ("")
        self._lock = asyncio.Lock()

    async def _send(self, p: SendParams) -> Exchange:
        authorizer = self.authorizer
        async with self._lock:
            if authorizer.should_renew_token():
                await authorizer.renew_token()

        used_token = authorizer.fetch_token()
        authorizer.prepare_requisition(p.requisition)

        xchg = await super()._send(p)

        maybe_invalid_token = xchg.response.status == 401
        if maybe_invalid_token and authorizer.can_renew_token():
            async with self._lock:
                if used_token.access_token == authorizer.fetch_token().access_token:
                    await authorizer.renew_token()

            authorizer.prepare_requisition(p.requisition)

            xchg = await super()._send(p)

        return xchg
