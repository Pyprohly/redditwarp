
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ....models.comment_SYNC import LooseComment
from ....model_loaders.comment_SYNC import load_loose_comment

class LooseCommentListingPaginator(ListingPaginator[LooseComment]):
    def fetch(self) -> Sequence[LooseComment]:
        data = self._fetch_data()
        return [load_loose_comment(d['data'], self.client) for d in data['children']]
