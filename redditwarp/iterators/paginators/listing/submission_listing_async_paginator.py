
from __future__ import annotations
from typing import Sequence

from .listing_async_paginator import ListingAsyncPaginator
from ....api.load.submission import load_submission
from ....models.submission import Submission

class SubmissionListingAsyncPaginator(ListingAsyncPaginator[Submission]):
    async def __anext__(self) -> Sequence[Submission]:
        data = await self._next_page_listing_data()
        return [load_submission(d) for d in data['children']]
