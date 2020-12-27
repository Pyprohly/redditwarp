
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, Any, Optional, Mapping, MutableMapping, Union, AnyStr
    from types import TracebackType
    from .base_session_ASYNC import BaseSession
    from .requestor_ASYNC import Requestor
    from .response import Response
    from .payload import RequestFiles

from .request import Request
from .payload import build_payload

class BaseHTTPClient:
    def __init__(self,
        session: BaseSession,
        *,
        params: Optional[MutableMapping[str, Optional[str]]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        self.session = session
        self.requestor: Requestor = session
        self.params: MutableMapping[str, Optional[str]]
        self.params = {} if params is None else params
        self.headers: MutableMapping[str, str]
        self.headers = {} if headers is None else headers

    async def __aenter__(self) -> BaseHTTPClient:
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
        timeout: float = 0,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Response:
        return await self.requestor.send(request, timeout=timeout, aux_info=aux_info)

    def build_request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], AnyStr]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
    ) -> Request:
        params = {} if params is None else params
        params = {**self.params, **params}
        remove_keys = [k for k, v in params.items() if v is NotImplemented]
        for k in remove_keys: del params[k]

        headers = {} if headers is None else headers
        headers = {**self.headers, **headers}

        payload = build_payload(data, json, files)
        return Request(verb, uri, params=params, payload=payload, headers=headers)

    async def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], AnyStr]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = 0,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Response:
        r = self.build_request(verb, uri, params=params, headers=headers,
                data=data, json=json, files=files)
        return await self.send(r, timeout=timeout, aux_info=aux_info)

    async def close(self) -> None:
        await self.session.close()
