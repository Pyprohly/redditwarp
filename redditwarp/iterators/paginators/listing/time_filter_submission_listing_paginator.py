
from __future__ import annotations
from typing import Sequence

from .time_filter_common_listing_paginator import TimeFilterCommonListingPaginator
from ....models.submission_SYNC import Submission
from ....api.load.submission_SYNC import load_submission

class TimeFilterSubmissionListingPaginator(TimeFilterCommonListingPaginator[Submission]):
    def _next_page(self) -> Sequence[Submission]:
        data = self._fetch_next_page_listing_data()
        return [load_submission(d['data'], self.client) for d in data['children']]
