
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, Any
if TYPE_CHECKING:
    from ..auth.token_obtainment_client_SYNC import TokenObtainmentClient
    from ..auth.token import Token
    from ..http.requestor_SYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

import time

from ..http.components.requestor_decorator_SYNC import RequestorDecorator
from .exceptions import UnknownTokenType
from ..auth.grants import RefreshTokenGrant

class Authorizer:
    """Knows how to authorize requests."""

    def __init__(self,
        token_client: Optional[TokenObtainmentClient],
        token: Optional[Token],
    ):
        self.token_client = token_client
        self.token = token
        self.expiry_skew = 30
        self.expiry_time: Optional[int] = None
        self.expires_in_fallback: Optional[int] = None

    def token_expired(self) -> bool:
        if self.expiry_time is None:
            return False
        return self.current_time() > self.expiry_time

    def can_renew_token(self) -> bool:
        return self.token_client is not None

    def renew_token(self) -> None:
        if self.token_client is None:
            raise RuntimeError('a new token was requested but no token client is assigned')

        self.token = tk = self.token_client.fetch_token()

        if tk.refresh_token is not None:
            self.token_client.grant = RefreshTokenGrant(tk.refresh_token)

        if tk.token_type.lower() != 'bearer':
            raise UnknownTokenType(token=tk)

        if tk.expires_in is None:
            if self.expires_in_fallback is None:
                self.expiry_time = None
            else:
                self.expiry_time = int(self.current_time()) + self.expires_in_fallback - self.expiry_skew
        else:
            self.expiry_time = int(self.current_time()) + tk.expires_in - self.expiry_skew

    def maybe_renew_token(self) -> None:
        """Attempt to renew the token if it is unavailable or has expired."""
        if (self.token is None) or self.token_expired():
            self.renew_token()

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
    """Used to perform requests to endpoints that require authorization."""

    def __init__(self, requestor: Requestor, authorizer: Authorizer) -> None:
        super().__init__(requestor)
        self.authorizer = authorizer

    def send(self, request: Request, *, timeout: float = -2,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        self.authorizer.maybe_renew_token()
        self.authorizer.prepare_request(request)

        response = self.requestor.send(request, timeout=timeout, aux_info=aux_info)

        if response.status == 401 and self.authorizer.can_renew_token():
            self.authorizer.renew_token()
            self.authorizer.prepare_request(request)

            response = self.requestor.send(request, timeout=timeout, aux_info=aux_info)

        return response
