
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Sequence
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ..listing.mixins.sort_SYNC import Sort
from ..listing.listing_paginator import ListingPaginator
from ....models.user_SYNC import User
from ....model_loaders.user_SYNC import load_user

class UserSearchPaginator(
    Sort[User],
    ListingPaginator[User],
):
    def __init__(self,
        client: Client,
        uri: str,
        query: str,
    ):
        super().__init__(client, uri)
        self.query: str = query

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('q', self.query)

    def fetch(self) -> Sequence[User]:
        data = self._fetch_data()
        return [load_user(d['data'], self.client) for d in data['children']]
