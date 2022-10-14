
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from typing import Any, Optional, Mapping, MutableMapping, Union
    from types import TracebackType
    from .session_base_SYNC import SessionBase
    from .requestor_SYNC import Requestor
    from .request import Request
    from .response import Response
    from .payload import RequestFiles

from urllib.parse import urljoin

from .request import make_request
from .util.case_insensitive_dict import CaseInsensitiveDict

T = TypeVar('T')

class HTTPClient:
    """A high-level object that wraps a HTTP session.

    The purpose of the HTTPClient is to be as useful as possible.
    """

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

    def __enter__(self: T) -> T:
        return self

    def __exit__(self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.close()
        return None

    def close(self) -> None:
        self.session.close()

    def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        return self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)

    def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = -2,
        follow_redirects: Optional[bool] = None,
    ) -> Response:
        r = self.make_request(verb, uri, params=params, headers=headers,
                data=data, json=json, files=files)
        return self.send(r, timeout=timeout, follow_redirects=follow_redirects)


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

    def _do_send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        return super().send(request, timeout=timeout, follow_redirects=follow_redirects)

    def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        self._prepare_request(request)
        return self._do_send(request, timeout=timeout, follow_redirects=follow_redirects)
