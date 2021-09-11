
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ....models.load.submission_SYNC import load_submission
from ....models.submission_SYNC import Submission

class SubmissionListingPaginator(ListingPaginator[Submission]):
    def next_result(self) -> Sequence[Submission]:
        data = self._next_data()
        return [load_submission(d['data'], self.client) for d in data['children']]
