
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Dict
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from .listing_async_paginator import ListingAsyncPaginator

T = TypeVar('T')

class TimeFilterListingAsyncPaginator(ListingAsyncPaginator[T]):
    def __init__(self, client: Client, uri: str):
        super().__init__(client, uri)
        self.time_filter: Optional[str] = None

    def _get_params(self) -> Dict[str, str]:
        params = super()._get_params()
        if self.time_filter is not None:
            params['t'] = self.time_filter
        return params
