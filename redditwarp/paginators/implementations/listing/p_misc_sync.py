
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Sequence
if TYPE_CHECKING:
    from ....client_SYNC import Client

from types import SimpleNamespace

from .mixins.sort_SYNC import Sort
from .listing_paginator import ListingPaginator


class NamespaceListingPaginator(ListingPaginator[SimpleNamespace]):
    def next_result(self) -> Sequence[SimpleNamespace]:
        data = self._next_data()
        return [SimpleNamespace(**d['data']) for d in data['children']]


class SearchUsersListingPaginator(
    Sort[SimpleNamespace],
    NamespaceListingPaginator,
):
    def __init__(self,
        client: Client,
        uri: str,
        query: str,
    ):
        super().__init__(client, uri)
        self.query = query

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('q', self.query)
