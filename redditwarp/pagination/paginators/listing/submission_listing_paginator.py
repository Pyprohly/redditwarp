
from __future__ import annotations
from typing import Sequence

from ..listing.listing_paginator import ListingPaginator
from ....model_loaders.submission_SYNC import load_submission
from ....models.submission_SYNC import Submission

class SubmissionListingPaginator(ListingPaginator[Submission]):
    def fetch(self) -> Sequence[Submission]:
        data = self._fetch_data()
        return [load_submission(d['data'], self.client) for d in data['children']]
