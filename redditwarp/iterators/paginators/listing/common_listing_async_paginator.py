
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Dict, Optional
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from .listing_async_paginator import ListingAsyncPaginator

T = TypeVar('T')

class CommonListingAsyncPaginator(ListingAsyncPaginator[T]):
    def __init__(self, client: Client, uri: str) -> None:
        super().__init__(client, uri)
        self.include_subreddit_data = False

    def _get_next_page_params(self) -> Dict[str, Optional[str]]:
        params = super()._get_next_page_params()
        if self.include_subreddit_data:
            params['sr_detail'] = '1'
        return params
