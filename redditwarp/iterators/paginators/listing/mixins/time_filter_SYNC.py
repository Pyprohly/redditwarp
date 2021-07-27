
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, MutableMapping, Callable, Any
if TYPE_CHECKING:
    from .....client_SYNC import Client

from ..listing_paginator import ListingPaginator

T = TypeVar('T')

class TimeFilter(ListingPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(client, uri, limit=limit, cursor_extractor=cursor_extractor)
        self.time_filter: str = ''

    def _get_params(self) -> MutableMapping[str, Optional[str]]:
        params = super()._get_params()
        if self.time_filter:
            params['t'] = self.time_filter
        return params
