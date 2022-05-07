
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Sequence
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ..listing.mixins.sort_ASYNC import Sort
from ..listing.listing_async_paginator import ListingAsyncPaginator
from ....models.user_ASYNC import User
from ....model_loaders.user_ASYNC import load_user

class SearchUsersListingAsyncPaginator(
    Sort[User],
    ListingAsyncPaginator[User],
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

    async def fetch(self) -> Sequence[User]:
        data = await self._fetch_data()
        return [load_user(d['data'], self.client) for d in data['children']]
