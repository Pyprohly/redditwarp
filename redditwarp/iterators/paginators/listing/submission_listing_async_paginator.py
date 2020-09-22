
from __future__ import annotations
from typing import Sequence

from .common_listing_async_paginator import CommonListingAsyncPaginator
from ....models.submission_ASYNC import Submission
from ....api.load.submission_ASYNC import load_submission

class SubmissionListingAsyncPaginator(CommonListingAsyncPaginator[Submission]):
    async def _next_page(self) -> Sequence[Submission]:
        data = await self._fetch_next_page_listing_data()
        return [load_submission(d['data'], self.client) for d in data['children']]
