
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Dict, Any
if TYPE_CHECKING:
    from ....client_SYNC import Client

from .common_listing_paginator import CommonListingPaginator

T = TypeVar('T')

class TimeFilterCommonListingPaginator(CommonListingPaginator[T]):
    def __init__(self, client: Client, uri: str) -> None:
        super().__init__(client, uri)
        self.time_filter: Optional[str] = None

    def _get_next_page_params(self) -> Dict[str, Any]:
        params = super()._get_next_page_params()
        if self.time_filter is not None:
            params['t'] = self.time_filter
        return params
