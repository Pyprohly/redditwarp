
from __future__ import annotations
from typing import Sequence

from .listing_async_paginator import ListingAsyncPaginator
from ...models.comment_ASYNC import ExtraSubmissionFieldsComment
from ...models.load.comment_ASYNC import load_extra_submission_fields_comment

class ExtraSubmissionFieldsCommentListingAsyncPaginator(ListingAsyncPaginator[ExtraSubmissionFieldsComment]):
    async def fetch_next(self) -> Sequence[ExtraSubmissionFieldsComment]:
        data = await self._fetch_next_data()
        return [load_extra_submission_fields_comment(d['data'], self.client) for d in data['children']]
