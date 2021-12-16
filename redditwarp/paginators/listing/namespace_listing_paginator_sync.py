
from __future__ import annotations
from typing import Sequence

from types import SimpleNamespace

from .listing_paginator import ListingPaginator


class NamespaceListingPaginator(ListingPaginator[SimpleNamespace]):
    def fetch_next(self) -> Sequence[SimpleNamespace]:
        data = self._fetch_next_data()
        return [SimpleNamespace(**d['data']) for d in data['children']]
