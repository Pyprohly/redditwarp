
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Dict, Callable, Any
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from .listing_async_paginator import ListingAsyncPaginator

T = TypeVar('T')

class TimeFilterListingAsyncPaginator(ListingAsyncPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(client, uri, limit=limit, cursor_extractor=cursor_extractor)
        self.time_filter: Optional[str] = None

    def _get_params(self) -> Dict[str, str]:
        params = super()._get_params()
        if self.time_filter is not None:
            params['t'] = self.time_filter
        return params
