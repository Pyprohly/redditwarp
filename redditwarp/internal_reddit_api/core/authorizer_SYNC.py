
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
if TYPE_CHECKING:
    from ..auth.internal_reddit_api_token_obtainment_client_SYNC import InternalRedditAPITokenObtainmentClient
    from ..auth.token import Token
    from ...http.handler_SYNC import Handler
    from ...http.requisition import Requisition
    from ...http.send_params import SendParams
    from ...http.exchange import Exchange

import time

from ...http.delegating_handler_SYNC import DelegatingHandler


def prepare_requisition(requisition: Requisition, token: Token, *,
        authorization_header_name: str = 'Authorization') -> None:
    requisition.headers[authorization_header_name] = 'Bearer {0.access_token}'.format(token)


class Authorizer:
    def __init__(self,
        token_client: Optional[InternalRedditAPITokenObtainmentClient] = None,
        token: Optional[Token] = None,
    ):
        self._token_client: Optional[InternalRedditAPITokenObtainmentClient] = token_client
        self._token: Optional[Token] = token
        self.renewal_time: Optional[int] = None
        self.renewal_skew: int = 30
        self.expires_in_fallback: Optional[int] = None
        self.time_func: Callable[[], float] = time.monotonic
        self.authorization_header_name: str = 'Authorization'

    def has_token_client(self) -> bool:
        return self._token_client is not None

    def get_token_client(self) -> InternalRedditAPITokenObtainmentClient:
        v = self._token_client
        if v is None:
            raise RuntimeError('token client not set')
        return v

    def set_token_client(self, value: Optional[InternalRedditAPITokenObtainmentClient]) -> None:
        self._token_client = value

    def has_token(self) -> bool:
        return self._token is not None

    def get_token(self) -> Token:
        v = self._token
        if v is None:
            raise RuntimeError('token not set')
        return v

    def set_token(self, value: Optional[Token]) -> None:
        self._token = value

    def renew_token(self) -> None:
        tc = self.get_token_client()

        tk = tc.fetch_token()
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
        return self.has_token_client()

    def prepare_requisition(self, requisition: Requisition) -> None:
        prepare_requisition(requisition, self.get_token(), authorization_header_name=self.authorization_header_name)


class Authorized(DelegatingHandler):
    def __init__(self, handler: Handler, authorizer: Authorizer) -> None:
        super().__init__(handler)
        self.authorizer: Authorizer = authorizer

    def _send(self, p: SendParams) -> Exchange:
        authorizer = self.authorizer
        if authorizer.should_renew_token():
            authorizer.renew_token()

        authorizer.prepare_requisition(p.requisition)

        xchg = super()._send(p)

        maybe_invalid_token = xchg.response.status == 401
        if maybe_invalid_token and authorizer.can_renew_token():
            authorizer.renew_token()

            authorizer.prepare_requisition(p.requisition)

            xchg = super()._send(p)

        return xchg
