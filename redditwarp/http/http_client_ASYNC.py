
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, final
if TYPE_CHECKING:
    from typing import Optional, Mapping, Union
    from types import TracebackType
    from .requisition import Requisition
    from .response import Response
    from .types import RequestFiles
    from .handler_ASYNC import Handler
    from .exchange import Exchange
    from ..types import JSON_ro
    from .payload import Payload

from urllib.parse import urljoin

from .requisition import make_requisition
from .send_params import SendParams
from .invoker_ASYNC import Invoker


DEFAULT_TIMEOUT: float = 100.


class HTTPClient:
    """A class for sending HTTP requests.

    The purpose of the HTTPClient is to be as useful as possible.
    """

    _TSelf = TypeVar('_TSelf', bound='HTTPClient')

    @staticmethod
    def make_requisition(
        verb: str,
        url: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: JSON_ro = None,
        files: Optional[RequestFiles] = None,
        payload: Optional[Payload] = None,
    ) -> Requisition:
        return make_requisition(
            verb,
            url,
            params=params,
            headers=headers,
            data=data,
            json=json,
            files=files,
            payload=payload,
        )

    def __init__(self, handler: Handler) -> None:
        self._invoker: Invoker = Invoker(handler)
        self.base_url: str = ''
        ("")
        self.timeout: float = DEFAULT_TIMEOUT
        ("")
        self.follow_redirects: Optional[bool] = False
        ("")

    async def __aenter__(self: _TSelf) -> _TSelf:
        return self

    async def __aexit__(self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    @final
    async def request(self,
        verb: str,
        url: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: JSON_ro = None,
        files: Optional[RequestFiles] = None,
        payload: Optional[Payload] = None,
        timeout: float = -2,
        follow_redirects: Optional[bool] = None,
    ) -> Response:
        xchg = await self.inquire(verb, url, params=params, headers=headers,
                data=data, json=json, files=files, payload=payload,
                timeout=timeout, follow_redirects=follow_redirects)
        return xchg.response

    @final
    async def inquire(self,
        verb: str,
        url: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: JSON_ro = None,
        files: Optional[RequestFiles] = None,
        payload: Optional[Payload] = None,
        timeout: float = -2,
        follow_redirects: Optional[bool] = None,
    ) -> Exchange:
        reqi = self.make_requisition(verb, url, params=params, headers=headers,
                data=data, json=json, files=files, payload=payload)
        return await self.submit(reqi, timeout=timeout, follow_redirects=follow_redirects)

    @final
    async def submit(self,
        reqi: Requisition,
        *,
        timeout: float = -2,
        follow_redirects: Optional[bool] = None,
    ) -> Exchange:
        p = SendParams(
            reqi,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )
        return await self._send(p)

    async def _send(self, p: SendParams) -> Exchange:
        reqi = p.requisition
        reqi.url = urljoin(self.base_url, reqi.url)
        if p.timeout == -2:
            p.timeout = self.timeout
        if p.follow_redirects is None:
            p.follow_redirects = self.follow_redirects
        return await self._invoker.send(p)

    async def close(self) -> None:
        await self._invoker.close()
