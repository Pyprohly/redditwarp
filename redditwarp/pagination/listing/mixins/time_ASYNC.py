
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Callable, Any, Iterable, Mapping
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ..listing_async_paginator import ListingAsyncPaginator

T = TypeVar('T')

class Time(ListingAsyncPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        params: Optional[Mapping[str, str]] = None,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(client, uri, limit=limit, params=params, cursor_extractor=cursor_extractor)
        self.time: str = ''

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        if self.time:
            yield ('t', self.time)
