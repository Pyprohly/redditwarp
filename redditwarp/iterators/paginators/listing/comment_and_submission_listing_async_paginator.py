
from __future__ import annotations
from typing import Sequence, Optional

from .listing_async_paginator import ListingAsyncPaginator
from ....models.original_reddit_thing_object import OriginalRedditThingObject
from ....models.load.comment_ASYNC import load_comment
from ....models.load.submission_ASYNC import load_submission

class CommentAndSubmissionListingAsyncPaginator(ListingAsyncPaginator[OriginalRedditThingObject]):
    async def _fetch_result(self) -> Sequence[OriginalRedditThingObject]:
        data = await self._fetch_data()
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
