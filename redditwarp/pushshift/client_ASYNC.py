
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Mapping, Any, Union
if TYPE_CHECKING:
    from ..http.http_client_ASYNC import HTTPClient
    from ..http.types import RequestFiles
    from ..http.payload import Payload
    from ..types import JSON_ro

from .core.http_client_ASYNC import build_http_client
from ..http.util.json_loading import load_json_from_response

class Client:
    _TSelf = TypeVar('_TSelf', bound='Client')

    @classmethod
    def from_http(cls: type[_TSelf], http: HTTPClient) -> _TSelf:
        self = cls.__new__(cls)
        self._init(http)
        return self

    def __init__(self) -> None:
        http = build_http_client()
        self._init(http)

    def _init(self, http: HTTPClient) -> None:
        self.http: HTTPClient = http
        ("")

        from .siteprocs.ASYNC import Procedures
        self.p: Procedures = Procedures(self)

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
    ) -> Any:
        json_data = None
        resp = await self.http.request(verb, url, params=params, headers=headers,
                data=data, json=json, files=files, payload=payload,
                timeout=timeout, follow_redirects=follow_redirects)
        if resp.data:
            json_data = load_json_from_response(resp)
        resp.ensure_successful_status()
        return json_data

PushshiftClient = Client
Pushshift = Client
PushshiftAPI = Client
