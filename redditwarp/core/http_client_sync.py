
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, Any, Optional, Mapping, MutableMapping
    from types import TracebackType
    from ..http.base_session_sync import BaseSession
    from .authorizer_sync import Authorizer, Authorized
    from ..http.requestor_sync import Requestor
    from ..http.response import Response
    from ..http.payload import Payload

import sys
from time import sleep

from .. import __about__
from .. import auth
from .exceptions import handle_auth_response_exception
from ..http.request import Request
from ..http.payload import make_payload

class RedditHTTPClient:
    TIMEOUT = 8

    @property
    def default_headers(self) -> MutableMapping[str, str]:
        return self._default_headers

    @property
    def user_agent(self) -> str:
        return self._default_headers['User-Agent']

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        self._default_headers['User-Agent'] = value

    @property
    def authorizer(self) -> Optional[Authorizer]:
        if self.authorized_requestor is None:
            return None
        return self.authorized_requestor.authorizer

    @authorizer.setter
    def authorizer(self, value: Authorizer) -> None:
        if self.authorized_requestor is None:
            raise RuntimeError('The client is not configured in a way that knows how update this field.')
        self.authorized_requestor.authorizer = value

    def __init__(self,
        session: BaseSession,
        requestor: Optional[Requestor],
        *,
        default_headers: Optional[MutableMapping[str, str]] = None,
        authorized_requestor: Optional[Authorized],
    ) -> None:
        self.session = session
        self.requestor = session if requestor is None else requestor
        self._default_headers = {} if default_headers is None else default_headers
        self.authorized_requestor = authorized_requestor
        self.user_agent = self.user_agent_string_head = (
            f"{__about__.__title__}/{__about__.__version__} "
            f"Python/{'.'.join(map(str, sys.version_info[:2]))} "
            f"{session.TRANSPORTER.name}/{session.TRANSPORTER.version}"
        )

    def __enter__(self) -> RedditHTTPClient:
        return self

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.close()
        return None

    def send(self,
        request: Request,
        timeout: float = TIMEOUT,
        aux_info: Optional[Mapping] = None,
    ) -> Response:
        for i in range(5):
            try:
                resp = self.requestor.send(request, timeout=timeout, aux_info=aux_info)

            except auth.exceptions.ResponseException as e:
                handle_auth_response_exception(e)

            if resp.status in (500, 502):
                sleep(i**2)
                continue
            break
        return resp

    def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[MutableMapping[str, Optional[str]]] = None,
        payload: Optional[Payload] = None,
        data: Any = None,
        json: Any = None,
        headers: Optional[MutableMapping[str, str]] = None,
        timeout: float = TIMEOUT,
        aux_info: Optional[Mapping] = None,
    ) -> Response:
        params = {} if params is None else params
        params.setdefault('raw_json', '1')
        params.setdefault('api_type', 'json')
        remove_keys = (k for k, v in params.items() if v is NotImplemented)
        for k in remove_keys: del params[k]

        payload = make_payload(payload, data, json)

        headers = {} if headers is None else headers
        headers.update({**self.default_headers, **headers})

        r = Request(verb, uri, params=params, payload=payload, headers=headers)
        return self.send(r, timeout=timeout, aux_info=aux_info)

    def close(self) -> None:
        self.session.close()

HTTPClient = RedditHTTPClient
