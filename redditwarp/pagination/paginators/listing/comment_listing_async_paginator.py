
from __future__ import annotations
from typing import Sequence

from .listing_async_paginator import ListingAsyncPaginator
from ....models.comment_ASYNC import ExtraSubmissionFieldsComment
from ....model_loaders.comment_ASYNC import load_extra_submission_fields_comment

class ExtraSubmissionFieldsCommentListingAsyncPaginator(ListingAsyncPaginator[ExtraSubmissionFieldsComment]):
    async def fetch(self) -> Sequence[ExtraSubmissionFieldsComment]:
        data = await self._fetch_data()
        return [load_extra_submission_fields_comment(d['data'], self.client) for d in data['children']]
