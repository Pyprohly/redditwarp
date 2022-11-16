
from __future__ import annotations
from typing import Sequence

from .listing_async_paginator import ListingAsyncPaginator
from ....models.comment_ASYNC import LooseComment
from ....model_loaders.comment_ASYNC import load_loose_comment

class LooseCommentListingAsyncPaginator(ListingAsyncPaginator[LooseComment]):
    async def fetch(self) -> Sequence[LooseComment]:
        data = await self._fetch_data()
        return [load_loose_comment(d['data'], self.client) for d in data['children']]
