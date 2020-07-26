
from __future__ import annotations
from typing import Sequence

from .time_filter_common_listing_async_paginator import TimeFilterCommonListingAsyncPaginator
from ....models.submission import Submission
from ....api.load.submission import load_submission

class TimeFilterSubmissionListingAsyncPaginator(TimeFilterCommonListingAsyncPaginator[Submission]):
    async def __anext__(self) -> Sequence[Submission]:
        data = await self._fetch_next_page_listing_data()
        return [load_submission(d) for d in data['children']]
