
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ....models.comment_SYNC import Comment
from ....api.load.comment_SYNC import load_comment

class CommentListingPaginator(ListingPaginator[Comment]):
    def _fetch_result(self) -> Sequence[Comment]:
        data = self._fetch_listing_data()
        return [load_comment(d['data'], self.client) for d in data['children']]
