
from __future__ import annotations
from typing import Sequence

from .time_filter_common_listing_paginator import TimeFilterCommonListingPaginator
from ....models.submission import Submission
from ....api.load.submission import load_submission

class TimeFilterSubmissionListingPaginator(TimeFilterCommonListingPaginator[Submission]):
    def __next__(self) -> Sequence[Submission]:
        data = self._fetch_next_page_listing_data()
        return [load_submission(d) for d in data['children']]
