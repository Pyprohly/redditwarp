
from __future__ import annotations
from typing import Sequence

from .common_listing_async_paginator import CommonListingAsyncPaginator
from ....models.submission import Submission
from ....api.load.submission import load_submission

class SubmissionListingAsyncPaginator(CommonListingAsyncPaginator[Submission]):
    async def __anext__(self) -> Sequence[Submission]:
        data = await self._fetch_next_page_listing_data()
        return [load_submission(d) for d in data['children']]