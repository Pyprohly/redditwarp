
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from typing import Any, Optional, Mapping, MutableMapping, Union
    from types import TracebackType
    from .session_base_ASYNC import SessionBase
    from .requestor_ASYNC import Requestor
    from .request import Request
    from .response import Response
    from .payload import RequestFiles

from urllib.parse import urljoin

from .request import make_request
from .util.case_insensitive_dict import CaseInsensitiveDict

T = TypeVar('T')

class HTTPClient:
    @staticmethod
    def make_request(
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
    ) -> Request:
        return make_request(
            verb,
            uri,
            params=params,
            headers=headers,
            data=data,
            json=json,
            files=files,
        )

    def __init__(self,
        session: SessionBase,
        requestor: Optional[Requestor] = None,
    ) -> None:
        self.session: SessionBase = session
        self.requestor: Requestor = session if requestor is None else requestor

    async def __aenter__(self: T) -> T:
        return self

    async def __aexit__(self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    async def close(self) -> None:
        await self.session.close()

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        return await self.requestor.send(request, timeout=timeout)

    async def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = -2,
    ) -> Response:
        r = self.make_request(verb, uri, params=params, headers=headers,
                data=data, json=json, files=files)
        return await self.send(r, timeout=timeout)


class BasicRequestDefaultsHTTPClient(HTTPClient):
    def __init__(self,
        session: SessionBase,
        requestor: Optional[Requestor] = None,
        *,
        params: Optional[MutableMapping[str, str]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        super().__init__(session, requestor)
        self.base_url: str = ''
        self.params: MutableMapping[str, str] = CaseInsensitiveDict() if params is None else params
        self.headers: MutableMapping[str, str] = CaseInsensitiveDict() if headers is None else headers

    def _prepare_request(self, request: Request) -> None:
        r = request
        r.uri = urljoin(self.base_url, r.uri)
        (_d0 := r.params).update({**self.params, **_d0})
        (_d1 := r.headers).update({**self.headers, **_d1})

    async def _do_send(self, request: Request, *, timeout: float = -2) -> Response:
        return await super().send(request, timeout=timeout)

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        self._prepare_request(request)
        return await self._do_send(request, timeout=timeout)
