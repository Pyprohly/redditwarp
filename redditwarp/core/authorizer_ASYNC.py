
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable, MutableMapping
if TYPE_CHECKING:
    from ..auth.token_obtainment_client_ASYNC import TokenObtainmentClient
    from ..auth.token import Token
    from ..http.handler_ASYNC import Handler
    from ..http.requisition import Requisition
    from ..http.send_params import SendParams
    from ..http.exchange import Exchange

from ..util.imports import lazy_import
if TYPE_CHECKING:
    import asyncio
else:
    lazy_import % 'asyncio'

import time

from ..http.delegating_handler_ASYNC import DelegatingHandler
from ..auth.exceptions import (
    UnknownTokenType,
    extract_www_authenticate_auth_params,
    raise_for_resource_server_response_error,
)


class Authorizer:
    """An object for managing the token.

    The `Authorizer` keeps token information and knows how to renew the token
    when it expires and how to prepare a requisition.
    """

    def __init__(self,
        token_client: Optional[TokenObtainmentClient] = None,
        token: Optional[Token] = None,
    ) -> None:
        self.token_client: Optional[TokenObtainmentClient] = token_client
        ("""
            A token obtainment client used to make the token obtainment requests.
            """)
        self.token: Optional[Token] = token
        ("""
            Holds the current token information.
            """)
        self.renewal_time: Optional[float] = None
        ("""
            Time at which the token is expected to expire. See :meth:`.time`.
            """)
        self.renewal_skew: float = 30
        ("""
            Number of seconds before the token expiration when the token should be renewed.
            """)
        self.expires_in_fallback: Optional[int] = None
        ("""
            A fallback value for the token expiration time when not specified by the server.
            """)
        self.time_func: Callable[[], float] = time.monotonic
        ("""
            A function that returns the current time. The :meth:`time` method calls this this function.
            """)
        self.authorization_header_name: str = 'Authorization'
        ("""
            Name of the `Authorization` header. Use this attribute to change its capitalization.
            """)

    def has_token_client(self) -> bool:
        return self.token_client is not None

    def fetch_token_client(self) -> TokenObtainmentClient:
        """Return `.token_client`. Raise `RuntimeError` if not set."""
        v = self.token_client
        if v is None:
            raise RuntimeError('token client not set')
        return v

    def set_token_client(self, value: Optional[TokenObtainmentClient]) -> None:
        """Set `.token_client`."""
        self.token_client = value

    def has_token(self) -> bool:
        return self.token is not None

    def fetch_token(self) -> Token:
        """Return `.token`. Raise `RuntimeError` if not set."""
        v = self.token
        if v is None:
            raise RuntimeError('token not set')
        return v

    def set_token(self, value: Optional[Token]) -> None:
        """Set `.token`."""
        self.token = value

    async def renew_token(self) -> None:
        """Renew the token.

        .. .RAISES

        :raises RuntimeError:
            No token client (:attr:`token_client`) is set.
        """
        tc = self.fetch_token_client()
        tk = await tc.fetch_token()
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
        """Return the current internal time. This is used for :attr:`renewal_time`."""
        return self.time_func()

    def should_renew_token(self) -> bool:
        """Return true if the token is expired, about to expire, or is unset."""
        if not self.has_token():
            return True
        if self.renewal_time is None:
            return False
        return self.time() >= self.renewal_time

    def can_renew_token(self) -> bool:
        """The token can be renewed if a token client (:attr:`token_client`) is available."""
        return self.has_token_client()

    async def attain_token(self) -> Token:
        if self.should_renew_token():
            await self.renew_token()
        return self.fetch_token()

    def get_header_entry(self) -> tuple[str, str]:
        """Return an authorization header entry tuple."""
        return (self.authorization_header_name, '{0.token_type} {0.access_token}'.format(self.fetch_token()))

    def prepare_requisition(self, requisition: Requisition) -> None:
        """Prepare a requisition for authorization using the token."""
        self.prepare_headers(requisition.headers)

    def prepare_headers(self, headers: MutableMapping[str, str]) -> None:
        """Update headers with an authorization entry."""
        k, v = self.get_header_entry()
        headers[k] = v


class Authorized(DelegatingHandler):
    """Used to make requests to endpoints that require authorization."""

    def __init__(self, handler: Handler, authorizer: Authorizer) -> None:
        super().__init__(handler)
        self.authorizer: Authorizer = authorizer
        self._lock = asyncio.Lock()

    async def _send(self, p: SendParams) -> Exchange:
        authorizer = self.authorizer
        async with self._lock:
            if authorizer.should_renew_token():
                await authorizer.renew_token()

        used_token = authorizer.fetch_token()
        authorizer.prepare_requisition(p.requisition)
        xchg = await super()._send(p)
        auth_params = extract_www_authenticate_auth_params(xchg.response)

        invalid_token = auth_params.get('error', '') == 'invalid_token'
        if invalid_token and authorizer.can_renew_token():
            async with self._lock:
                if used_token.access_token == authorizer.fetch_token().access_token:
                    await authorizer.renew_token()

            authorizer.prepare_requisition(p.requisition)
            xchg = await super()._send(p)
            auth_params = extract_www_authenticate_auth_params(xchg.response)

        raise_for_resource_server_response_error(auth_params)

        return xchg
