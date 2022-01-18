
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ...models.comment_SYNC import ExtraSubmissionFieldsComment
from ...models.load.comment_SYNC import load_extra_submission_fields_comment

class ExtraSubmissionFieldsCommentListingPaginator(ListingPaginator[ExtraSubmissionFieldsComment]):
    def fetch(self) -> Sequence[ExtraSubmissionFieldsComment]:
        data = self._fetch_data()
        return [load_extra_submission_fields_comment(d['data'], self.client) for d in data['children']]
