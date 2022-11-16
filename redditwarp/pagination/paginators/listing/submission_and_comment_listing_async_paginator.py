
from __future__ import annotations
from typing import Sequence, Optional

from ..listing.listing_async_paginator import ListingAsyncPaginator
from ....model_loaders.comment_ASYNC import load_loose_comment
from ....model_loaders.submission_ASYNC import load_submission
from ....exceptions import UnexpectedResultException

class SubmissionAndLooseCommentListingAsyncPaginator(ListingAsyncPaginator[object]):
    async def fetch(self) -> Sequence[object]:
        data = await self._fetch_data()
        l = []
        for child in data['children']:
            kind = child['kind']
            data = child['data']
            obj: Optional[object] = None
            if kind == 't1':
                obj = load_loose_comment(data, self.client)
            elif kind == 't3':
                obj = load_submission(data, self.client)
            if obj is None:
                raise UnexpectedResultException(f'unexpected kind {kind!r}')
            l.append(obj)
        return l
