
from __future__ import annotations
from typing import Sequence, Optional

from ..listing.listing_paginator import ListingPaginator
from ...models.load.comment_SYNC import load_extra_submission_fields_comment
from ...models.load.submission_SYNC import load_submission

class SubmissionAndExtraSubmissionFieldsCommentListingPaginator(ListingPaginator[object]):
    def fetch_next(self) -> Sequence[object]:
        data = self._fetch_next_data()
        l = []
        for child in data['children']:
            kind = child['kind']
            data = child['data']
            obj: Optional[object] = None
            if kind == 't1':
                obj = load_extra_submission_fields_comment(data, self.client)
            elif kind == 't3':
                obj = load_submission(data, self.client)
            if obj is None:
                raise ValueError(f'unexpected kind {kind!r}')
            l.append(obj)
        return l
