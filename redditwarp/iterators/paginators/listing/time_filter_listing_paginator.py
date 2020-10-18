
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Dict
if TYPE_CHECKING:
    from ....client_SYNC import Client

from .listing_paginator import ListingPaginator

T = TypeVar('T')

class TimeFilterListingPaginator(ListingPaginator[T]):
    def __init__(self, client: Client, uri: str):
        super().__init__(client, uri)
        self.time_filter: Optional[str] = None

    def _get_params(self) -> Dict[str, str]:
        params = super()._get_params()
        if self.time_filter is not None:
            params['t'] = self.time_filter
        return params
