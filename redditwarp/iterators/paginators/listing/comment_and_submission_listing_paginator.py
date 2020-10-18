
from __future__ import annotations
from typing import Sequence, Optional

from .listing_paginator import ListingPaginator
from ....models.original_reddit_thing_object import OriginalRedditThingObject
from ....api.load.comment_SYNC import load_comment
from ....api.load.submission_SYNC import load_submission

class CommentAndSubmissionListingPaginator(ListingPaginator[OriginalRedditThingObject]):
    def _fetch_result(self) -> Sequence[OriginalRedditThingObject]:
        data = self._fetch_listing_data()
        l = []
        for child in data['children']:
            kind = child['kind']
            data = child['data']
            obj: Optional[OriginalRedditThingObject] = None
            if kind == 't1':
                obj = load_comment(data, self.client)
            elif kind == 't3':
                obj = load_submission(data, self.client)
            if obj is None:
                raise ValueError(f'unexpected kind {kind!r}')
            l.append(obj)
        return l
