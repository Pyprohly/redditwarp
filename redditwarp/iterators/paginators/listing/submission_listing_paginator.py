
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ....api.load.submission import load_submission
from ....models.submission import Submission

class SubmissionListingPaginator(ListingPaginator[Submission]):
    def __next__(self) -> Sequence[Submission]:
        data = self._next_page_listing_data()
        return [load_submission(d) for d in data['children']]
