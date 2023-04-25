
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from ..core.http_client_ASYNC import HTTPClient

from .core.http_client_ASYNC import build_reddit_http_client


class Client:
    _TSelf = TypeVar('_TSelf', bound='Client')

    @classmethod
    def from_http(cls: type[_TSelf], http: HTTPClient) -> _TSelf:
        self = cls.__new__(cls)
        self._init(http)
        return self

    def __init__(self) -> None:
        http = build_reddit_http_client()
        self._init(http)

    def _init(self, http: HTTPClient) -> None:
        self.http: HTTPClient = http
        ("")

        from .siteprocs.ASYNC import Procedures
        self.p: Procedures = Procedures(self.http)

DarkClient = Client
