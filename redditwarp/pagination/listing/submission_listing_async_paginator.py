
from __future__ import annotations
from typing import Sequence

from ..listing.listing_async_paginator import ListingAsyncPaginator
from ...models.load.submission_ASYNC import load_submission
from ...models.submission_ASYNC import Submission

class SubmissionListingAsyncPaginator(ListingAsyncPaginator[Submission]):
    async def fetch(self) -> Sequence[Submission]:
        data = await self._fetch_data()
        return [load_submission(d['data'], self.client) for d in data['children']]
