
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
if TYPE_CHECKING:
    from ..auth.token_obtainment_client_SYNC import TokenObtainmentClient
    from ..auth.token import Token
    from ..http.requestor_SYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

import time

from ..http.requestor_augmenter_SYNC import RequestorAugmenter
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
        self.token_client: Optional[TokenObtainmentClient] = token_client
        self.token: Optional[Token] = token
        self.renewal_time: Optional[int] = None
        self.renewal_skew: int = 30
        self.expires_in_fallback: Optional[int] = None
        self.time_func: Callable[[], float] = time.monotonic

    def time(self) -> float:
        return self.time_func()

    def renew_token(self) -> None:
        if self.token_client is None:
            raise RuntimeError('no token client')

        self.token = tk = self.token_client.fetch_token()

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
            self.renewal_time = int(self.time()) + expires_in - self.renewal_skew

    def should_renew_token(self) -> bool:
        if self.token is None:
            return True
        if self.renewal_time is None:
            return False
        return self.time() >= self.renewal_time

    def can_renew_token(self) -> bool:
        return self.token_client is not None

    def prepare_request(self, request: Request) -> None:
        tk = self.token
        if tk is None:
            raise RuntimeError('no token is set')
        request.headers['Authorization'] = f'{tk.token_type} {tk.access_token}'


class Authorized(RequestorAugmenter):
    """Used to perform requests to endpoints that require authorization."""

    def __init__(self, requestor: Requestor, authorizer: Authorizer) -> None:
        super().__init__(requestor)
        self.authorizer: Authorizer = authorizer

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        authorizer = self.authorizer
        if authorizer.should_renew_token():
            authorizer.renew_token()
        authorizer.prepare_request(request)

        resp = self.requestor.send(request, timeout=timeout)

        auth_params = extract_www_authenticate_auth_params(resp)
        invalid_token = auth_params.get('error', '') == 'invalid_token'

        if invalid_token and authorizer.can_renew_token():
            authorizer.renew_token()
            authorizer.prepare_request(request)

            resp = self.requestor.send(request, timeout=timeout)

            auth_params = extract_www_authenticate_auth_params(resp)

        raise_for_resource_server_response_error(auth_params)

        return resp
