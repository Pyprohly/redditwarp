
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Dict, Any
if TYPE_CHECKING:
    from ....client_SYNC import Client

from .listing_paginator import ListingPaginator

T = TypeVar('T')

class CommonListingPaginator(ListingPaginator[T]):
    def __init__(self, client: Client, uri: str) -> None:
        super().__init__(client, uri)
        self.include_subreddit_data = False

    def _get_next_page_params(self) -> Dict[str, Any]:
        params = super()._get_next_page_params()
        if self.include_subreddit_data:
            params['sr_detail'] = '1'
        return params
