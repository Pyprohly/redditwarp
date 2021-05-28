
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from typing import Type, Any, Optional, Mapping, MutableMapping, Union, AnyStr
    from types import TracebackType
    from .session_base_SYNC import SessionBase
    from .response import Response
    from .payload import RequestFiles

from .request import Request
from .payload import make_payload

T = TypeVar('T')

class HTTPClientBase:
    def __init__(self,
        session: SessionBase,
        *,
        params: Optional[MutableMapping[str, Optional[str]]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        self.session = session
        self.params: MutableMapping[str, Optional[str]]
        self.params = {} if params is None else params
        self.headers: MutableMapping[str, str]
        self.headers = {} if headers is None else headers

    def __enter__(self: T) -> T:
        return self

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.close()
        return None

    def send(self, request: Request, *, timeout: float = -2,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        return self.session.send(request, timeout=timeout, aux_info=aux_info)

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

    def request(self,
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
        return self.send(r, timeout=timeout, aux_info=aux_info)

    def close(self) -> None:
        self.session.close()