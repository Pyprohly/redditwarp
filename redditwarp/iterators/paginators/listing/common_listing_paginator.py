
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Dict, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client

from .listing_paginator import ListingPaginator

T = TypeVar('T')

class CommonListingPaginator(ListingPaginator[T]):
    def __init__(self, client: Client, uri: str) -> None:
        super().__init__(client, uri)
        self.include_sr_detail = False

    def _get_next_page_params(self) -> Dict[str, Optional[str]]:
        params = super()._get_next_page_params()
        if self.include_sr_detail:
            params['sr_detail'] = '1'
        return params
