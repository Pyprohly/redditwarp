
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
if TYPE_CHECKING:
    from ..auth.token_obtainment_client_SYNC import TokenObtainmentClient
    from ..auth.token import Token
    from ..http.handler_SYNC import Handler
    from ..http.requisition import Requisition
    from ..http.send_params import SendParams
    from ..http.exchange import Exchange

import time

from ..http.delegating_handler_SYNC import DelegatingHandler
from ..auth.exceptions import (
    UnknownTokenType,
    extract_www_authenticate_auth_params,
    raise_for_resource_server_response_error,
)


def prepare_requisition(requisition: Requisition, token: Token, *,
        authorization_header_name: str = 'Authorization') -> None:
    """Prepare a requisition for authorization.

    This function sets the `Authorization` header using the token.
    """
    requisition.headers[authorization_header_name] = '{0.token_type} {0.access_token}'.format(token)


class Authorizer:
    """An object for managing the token.

    The `Authorizer` keeps token information and knows how to renew the token
    when it expires and how to prepare a requisition.
    """

    def __init__(self,
        token_client: Optional[TokenObtainmentClient] = None,
        token: Optional[Token] = None,
    ):
        self.token_client: Optional[TokenObtainmentClient] = token_client
        self.token: Optional[Token] = token
        self.renewal_time: Optional[float] = None
        self.renewal_skew: float = 30
        self.expires_in_fallback: Optional[int] = None
        self.time_func: Callable[[], float] = time.monotonic
        self.authorization_header_name: str = 'Authorization'

    def has_token_client(self) -> bool:
        return self.token_client is not None

    def fetch_token_client(self) -> TokenObtainmentClient:
        v = self.token_client
        if v is None:
            raise RuntimeError('token client not set')
        return v

    def set_token_client(self, value: Optional[TokenObtainmentClient]) -> None:
        self.token_client = value

    def has_token(self) -> bool:
        return self.token is not None

    def fetch_token(self) -> Token:
        v = self.token
        if v is None:
            raise RuntimeError('token not set')
        return v

    def set_token(self, value: Optional[Token]) -> None:
        self.token = value

    def renew_token(self) -> None:
        """Renew the token.

        .. RAISES

        :raises RuntimeError:
            There is no token client set.
        """
        tc = self.fetch_token_client()
        tk = tc.fetch_token()
        if tk.token_type.lower() != 'bearer':
            raise UnknownTokenType(token=tk)

        self.set_token(tk)

        expires_in = tk.expires_in
        if expires_in is None:
            expires_in = self.expires_in_fallback
        if expires_in is None:
            self.renewal_time = None
        else:
            self.renewal_time = self.time() + expires_in - self.renewal_skew

        if tk.refresh_token:
            grant1 = tc.grant
            if (
                grant1.get('grant_type', '') == 'refresh_token'
                and grant1.get('refresh_token', '') != tk.refresh_token
            ):
                tc.grant = {**grant1, 'refresh_token': tk.refresh_token}

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
        prepare_requisition(requisition, self.fetch_token(), authorization_header_name=self.authorization_header_name)


class Authorized(DelegatingHandler):
    """Used to make requests to endpoints that require authorization."""

    def __init__(self, handler: Handler, authorizer: Authorizer) -> None:
        super().__init__(handler)
        self.authorizer: Authorizer = authorizer

    def _send(self, p: SendParams) -> Exchange:
        authorizer = self.authorizer
        if authorizer.should_renew_token():
            authorizer.renew_token()

        authorizer.prepare_requisition(p.requisition)
        xchg = super()._send(p)
        auth_params = extract_www_authenticate_auth_params(xchg.response)

        invalid_token = auth_params.get('error', '') == 'invalid_token'
        if invalid_token and authorizer.can_renew_token():
            authorizer.renew_token()
            authorizer.prepare_requisition(p.requisition)
            xchg = super()._send(p)
            auth_params = extract_www_authenticate_auth_params(xchg.response)

        raise_for_resource_server_response_error(auth_params)

        return xchg
