
from __future__ import annotations
from typing import Sequence

from .time_filter_common_listing_async_paginator import TimeFilterCommonListingAsyncPaginator
from ....models.submission_ASYNC import Submission
from ....api.load.submission_ASYNC import load_submission

class TimeFilterSubmissionListingAsyncPaginator(TimeFilterCommonListingAsyncPaginator[Submission]):
    async def _next_page(self) -> Sequence[Submission]:
        data = await self._fetch_next_page_listing_data()
        return [load_submission(d['data'], self.client) for d in data['children']]
