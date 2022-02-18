
from __future__ import annotations
from typing import Sequence, Optional

from ..listing.listing_async_paginator import ListingAsyncPaginator
from ...models.load.comment_ASYNC import load_extra_submission_fields_comment
from ...models.load.submission_ASYNC import load_submission
from ...exceptions import UnexpectedResultException

class SubmissionAndExtraSubmissionFieldsCommentListingAsyncPaginator(ListingAsyncPaginator[object]):
    async def fetch(self) -> Sequence[object]:
        data = await self._fetch_data()
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
                raise UnexpectedResultException(f'unexpected kind {kind!r}')
            l.append(obj)
        return l
