
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ....models.submission_SYNC import Submission
from ....api.load.submission_SYNC import load_submission

class SubmissionListingPaginator(ListingPaginator[Submission]):
    def _fetch_result(self) -> Sequence[Submission]:
        data = self._fetch_listing_data()
        return [load_submission(d['data'], self.client) for d in data['children']]
