
from __future__ import annotations
from typing import Sequence

from .listing_async_paginator import ListingAsyncPaginator
from ....models.submission_ASYNC import Submission
from ....api.load.submission_ASYNC import load_submission

class SubmissionListingAsyncPaginator(ListingAsyncPaginator[Submission]):
    async def _fetch_result(self) -> Sequence[Submission]:
        data = await self._fetch_listing_data()
        return [load_submission(d['data'], self.client) for d in data['children']]
