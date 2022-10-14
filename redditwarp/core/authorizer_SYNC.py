
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
if TYPE_CHECKING:
    from ..auth.token_obtainment_client_SYNC import TokenObtainmentClient
    from ..http.requestor_SYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

import time

from ..auth.token import Token
from ..http.requestor_augmenter_SYNC import RequestorAugmenter
from ..auth.exceptions import (
    UnknownTokenType,
    extract_www_authenticate_auth_params,
    raise_for_resource_server_response_error,
)


def prepare_request(request: Request, token: Token, *,
        authorization_header_name: str = 'Authorization') -> None:
    """Prepare a request for authorization.

    This function sets the `Authorization` header using the token.
    """
    request.headers[authorization_header_name] = '{0.token_type} {0.access_token}'.format(token)


class Authorizer:
    """An object for managing the token.

    The `Authorizer` keeps token information and knows how to renew the token
    when it expires and how to prepare a request.
    """

    def __init__(self,
        token_client: Optional[TokenObtainmentClient] = None,
        token: Optional[Token] = None,
    ):
        self.token_client: Optional[TokenObtainmentClient] = token_client
        self._token: Optional[Token] = token
        self.renewal_time: Optional[int] = None
        self.renewal_skew: int = 30
        self.expires_in_fallback: Optional[int] = None
        self.time_func: Callable[[], float] = time.monotonic
        self.authorization_header_name: str = 'Authorization'

    def has_token(self) -> bool:
        return self._token is not None

    def get_token(self) -> Token:
        tk = self._token
        if tk is None:
            raise RuntimeError('token not set')
        return tk

    def set_token(self, token: Token) -> None:
        self._token = token

    def renew_token(self) -> None:
        """Renew the token.

        .. RAISES

        :raises RuntimeError:
            There is no token client set.
        """
        if self.token_client is None:
            raise RuntimeError('no token client')

        tk = self.token_client.fetch_token()

        if tk.token_type.lower() != 'bearer':
            raise UnknownTokenType(token=tk)

        self.set_token(tk)

        expires_in: Optional[int] = tk.expires_in
        if expires_in is None:
            expires_in = self.expires_in_fallback
        if expires_in is None:
            self.renewal_time = None
        else:
            self.renewal_time = int(self.time()) + expires_in - self.renewal_skew

        if tk.refresh_token:
            grant1 = self.token_client.grant
            if (
                grant1.get('grant_type', '') == 'refresh_token'
                and grant1.get('refresh_token', '') != tk.refresh_token
            ):
                self.token_client.grant = {**grant1, 'refresh_token': tk.refresh_token}

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
    """Used to perform requests to endpoints that require authorization."""

    def __init__(self, requestor: Requestor, authorizer: Authorizer) -> None:
        super().__init__(requestor)
        self.authorizer: Authorizer = authorizer

    def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        authorizer = self.authorizer
        if authorizer.should_renew_token():
            authorizer.renew_token()

        authorizer.prepare_request(request)
        resp = self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)
        auth_params = extract_www_authenticate_auth_params(resp)

        invalid_token = auth_params.get('error', '') == 'invalid_token'
        if invalid_token and authorizer.can_renew_token():
            authorizer.renew_token()
            authorizer.prepare_request(request)
            resp = self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)
            auth_params = extract_www_authenticate_auth_params(resp)

        raise_for_resource_server_response_error(auth_params)

        return resp
