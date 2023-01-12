
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from .listing.listing_async_paginator import ListingAsyncPaginator
from ...models.wiki_ASYNC import WikiPageRevision
from ...model_loaders.wiki_ASYNC import load_wiki_page_revision

class WikiPageRevisionsAsyncPaginator(ListingAsyncPaginator[WikiPageRevision]):
    def __init__(self,
        client: Client,
        url: str,
        *,
        limit: Optional[int] = 100,
    ) -> None:
        cursor_extractor = lambda x: ('WikiRevision_' + x['id'])
        super().__init__(client, url, limit=limit, cursor_extractor=cursor_extractor)

    async def fetch(self) -> Sequence[WikiPageRevision]:
        data = await self._fetch_data()
        return [load_wiki_page_revision(d, self.client) for d in data['children']]
