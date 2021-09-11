
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable
if TYPE_CHECKING:
    from ....client_SYNC import Client

from types import SimpleNamespace

from .mixins.sort_SYNC import Sort
from .namespace_listing_paginator_sync import NamespaceListingPaginator

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

    def _generate_params(self) -> Iterable[tuple[str, Optional[str]]]:
        yield from super()._generate_params()
        yield ('q', self.query)
