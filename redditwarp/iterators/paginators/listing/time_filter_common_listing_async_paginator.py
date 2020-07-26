
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Dict, Any
if TYPE_CHECKING:
    from ....client_sync import Client

from .common_listing_async_paginator import CommonListingAsyncPaginator

T = TypeVar('T')

class TimeFilterCommonListingAsyncPaginator(CommonListingAsyncPaginator[T]):
    def __init__(self, client: Client, uri: str) -> None:
        super().__init__(client, uri)
        self.time_filter: Optional[str] = None

    def _get_next_page_params(self) -> Dict[str, Any]:
        params = super()._get_next_page_params()
        if self.time_filter is not None:
            params['t'] = self.time_filter
        return params
