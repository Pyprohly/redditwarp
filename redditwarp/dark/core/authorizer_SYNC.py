
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable, MutableMapping
if TYPE_CHECKING:
    from ..auth.token_obtainment_client_SYNC import TokenObtainmentClient
    from ..auth.token import Token
    from ...http.handler_SYNC import Handler
    from ...http.requisition import Requisition
    from ...http.send_params import SendParams
    from ...http.exchange import Exchange

import time

from ...http.delegating_handler_SYNC import DelegatingHandler


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

    def renew_token(self) -> None:
        tc = self.fetch_token_client()
        tk = tc.fetch_token()

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

    def attain_token(self) -> Token:
        if self.should_renew_token():
            self.renew_token()
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
