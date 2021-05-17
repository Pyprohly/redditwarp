
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from typing import Type, Any, Optional, Mapping, MutableMapping, Union, AnyStr
    from types import TracebackType
    from .base_session_ASYNC import BaseSession
    from .response import Response
    from .payload import RequestFiles

from .request import Request
from .payload import make_payload
from .requestor_decorator_ASYNC import RequestorDecorator

T = TypeVar('T')

class BaseHTTPClient(RequestorDecorator):
    def __init__(self,
        session: BaseSession,
        *,
        params: Optional[MutableMapping[str, Optional[str]]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        super().__init__(session)
        self.session = session
        self.params: MutableMapping[str, Optional[str]]
        self.params = {} if params is None else params
        self.headers: MutableMapping[str, str]
        self.headers = {} if headers is None else headers

    async def __aenter__(self: T) -> T:
        return self

    async def __aexit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    async def send(self, request: Request, *, timeout: float = -2,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        return await self.requestor.send(request, timeout=timeout, aux_info=aux_info)

    def _new_request(self,
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

        payload = make_payload(data, json, files)
        return Request(verb, uri, params=params, headers=headers, payload=payload)

    async def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], AnyStr]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = -2,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Response:
        r = self._new_request(verb, uri, params=params, headers=headers,
                data=data, json=json, files=files)
        return await self.send(r, timeout=timeout, aux_info=aux_info)

    async def close(self) -> None:
        await self.session.close()
