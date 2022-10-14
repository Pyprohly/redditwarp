
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
if TYPE_CHECKING:
    from ..auth.reddit_internal_api_token_obtainment_client_ASYNC import RedditInternalAPITokenObtainmentClient
    from ..auth.token import Token
    from ...http.requestor_ASYNC import Requestor
    from ...http.request import Request
    from ...http.response import Response

from ...util.imports import lazy_import
if TYPE_CHECKING:
    import asyncio
else:
    lazy_import % 'asyncio'

import time

from ...http.requestor_augmenter_ASYNC import RequestorAugmenter


def prepare_request(request: Request, token: Token, *,
        authorization_header_name: str = 'Authorization') -> None:
    request.headers[authorization_header_name] = 'Bearer {0.access_token}'.format(token)


class Authorizer:
    def __init__(self,
        token_client: Optional[RedditInternalAPITokenObtainmentClient] = None,
        token: Optional[Token] = None,
    ):
        self.token_client: Optional[RedditInternalAPITokenObtainmentClient] = token_client
        self._token: Optional[Token] = token
        self.renewal_time: Optional[int] = None
        self.renewal_skew: int = 30
        self.expires_in_fallback: Optional[int] = None
        self.time_func: Callable[[], float] = time.monotonic
        self.authorization_header_name: str = 'Authorization'

    def has_token(self) -> bool:
        return self._token is not None

    def get_token(self) -> Token:
        if (tk := self._token) is not None:
            return tk
        raise RuntimeError('token not set')

    def set_token(self, token: Token) -> None:
        self._token = token

    async def renew_token(self) -> None:
        if self.token_client is None:
            raise RuntimeError('no token client')

        tk = await self.token_client.fetch_token()
        self.set_token(tk)

        expires_in: Optional[int] = tk.expires_in
        if expires_in is None:
            expires_in = self.expires_in_fallback
        if expires_in is None:
            self.renewal_time = None
        else:
            self.renewal_time = int(self.time()) + expires_in - self.renewal_skew

    def time(self) -> float:
        return self.time_func()

    def should_renew_token(self) -> bool:
        if not self.has_token():
            return True
        if self.renewal_time is None:
            return False
        return self.time() >= self.renewal_time

    def can_renew_token(self) -> bool:
        return self.token_client is not None

    def prepare_request(self, request: Request) -> None:
        prepare_request(request, self.get_token(), authorization_header_name=self.authorization_header_name)


class Authorized(RequestorAugmenter):
    def __init__(self, requestor: Requestor, authorizer: Authorizer) -> None:
        super().__init__(requestor)
        self.authorizer: Authorizer = authorizer
        self._lock = asyncio.Lock()

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        authorizer = self.authorizer
        async with self._lock:
            if authorizer.should_renew_token():
                await authorizer.renew_token()

        used_token = authorizer.get_token()
        authorizer.prepare_request(request)

        resp = await self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)

        maybe_invalid_token = resp.status == 401
        if maybe_invalid_token and authorizer.can_renew_token():
            async with self._lock:
                if used_token.access_token == authorizer.get_token().access_token:
                    await authorizer.renew_token()

            authorizer.prepare_request(request)

            resp = await self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)

        return resp
