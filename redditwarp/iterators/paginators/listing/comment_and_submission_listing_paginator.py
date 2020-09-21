
from __future__ import annotations
from typing import Sequence, Optional

from .common_listing_paginator import CommonListingPaginator
from ....models.comment_SYNC import Comment
from ....models.original_reddit_thing_object import OriginalRedditThingObject
from ....api.load.submission_SYNC import load_submission

class CommentAndSubmissionListingPaginator(CommonListingPaginator[OriginalRedditThingObject]):
    def __next__(self) -> Sequence[OriginalRedditThingObject]:
        data = self._fetch_next_page_listing_data()
        l = []
        for child in data['children']:
            kind = child['kind']
            data = child['data']
            obj: Optional[OriginalRedditThingObject] = None
            if kind == 't1':
                obj = Comment(data, self._client)
            elif kind == 't3':
                obj = load_submission(data, self._client)
            if obj is None:
                raise ValueError(f'cannot handle kind {kind!r}')
            l.append(obj)
        return l
