
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, Any, Optional, Mapping, MutableMapping
    from types import TracebackType
    from ..http.base_session_ASYNC import BaseSession
    from .authorizer_ASYNC import Authorizer, Authorized
    from ..http.requestor_ASYNC import Requestor
    from ..http.response import Response
    from ..http.payload import Payload

import sys

from .. import __about__
from .. import auth
from .exceptions import handle_auth_response_exception
from ..http.request import Request
from ..http.payload import make_payload

class RedditHTTPClient:
    TIMEOUT = 8
    DEFAULT_PARAMS = {
        'raw_json': '1',
        'api_type': 'json',
    }

    @property
    def user_agent(self) -> str:
        return self.headers['User-Agent']

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        self.headers['User-Agent'] = value

    @property
    def authorizer(self) -> Optional[Authorizer]:
        if self.authorized_requestor is None:
            return None
        return self.authorized_requestor.authorizer

    @authorizer.setter
    def authorizer(self, value: Authorizer) -> None:
        if self.authorized_requestor is None:
            raise RuntimeError('The client is not configured in a way that knows how to update this field.')
        self.authorized_requestor.authorizer = value

    def __init__(self,
        session: BaseSession,
        *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        self.session = session
        self.requestor: Requestor = session
        self.authorized_requestor: Optional[Authorized] = None
        self.params = self.DEFAULT_PARAMS if params is None else params
        self.headers = {} if headers is None else headers
        self.user_agent = self.user_agent_string_head = (
            f"{__about__.__title__}/{__about__.__version__} "
            f"Python/{'.'.join(map(str, sys.version_info[:2]))} "
            f"{session.TRANSPORTER_INFO.name}/{session.TRANSPORTER_INFO.version}"
        )

    async def __aenter__(self) -> RedditHTTPClient:
        return self

    async def __aexit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    async def send(self,
        request: Request,
        timeout: float = TIMEOUT,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Response:
        try:
            resp = await self.requestor.send(request, timeout=timeout, aux_info=aux_info)
        except auth.exceptions.ResponseException as e:
            handle_auth_response_exception(e)
        return resp

    async def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[MutableMapping[str, Optional[str]]] = None,
        payload: Optional[Payload] = None,
        data: Any = None,
        json: Any = None,
        headers: Optional[MutableMapping[str, str]] = None,
        timeout: float = TIMEOUT,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Response:
        params = {} if params is None else params
        params = {**self.params, **params}
        remove_keys = [k for k, v in params.items() if v is NotImplemented]
        for k in remove_keys: del params[k]
        headers = {} if headers is None else headers
        headers = {**self.headers, **headers}

        payload = make_payload(payload, data, json)

        r = Request(verb, uri, params=params, payload=payload, headers=headers)
        return await self.send(r, timeout=timeout, aux_info=aux_info)

    async def close(self) -> None:
        await self.session.close()

HTTPClient = RedditHTTPClient
