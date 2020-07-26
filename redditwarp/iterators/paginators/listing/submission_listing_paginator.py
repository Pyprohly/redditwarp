
from __future__ import annotations
from typing import Sequence

from .common_listing_paginator import CommonListingPaginator
from ....models.submission import Submission
from ....api.load.submission import load_submission

class SubmissionListingPaginator(CommonListingPaginator[Submission]):
    def __next__(self) -> Sequence[Submission]:
        data = self._fetch_next_page_listing_data()
        return [load_submission(d) for d in data['children']]
