
from __future__ import annotations
from typing import Sequence, Optional

from .common_listing_async_paginator import CommonListingAsyncPaginator
from ....models.comment_ASYNC import Comment
from ....models.original_reddit_thing_object import OriginalRedditThingObject
from ....api.load.submission_ASYNC import load_submission

class CommentAndSubmissionListingAsyncPaginator(CommonListingAsyncPaginator[OriginalRedditThingObject]):
    async def __anext__(self) -> Sequence[OriginalRedditThingObject]:
        data = await self._fetch_next_page_listing_data()
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
