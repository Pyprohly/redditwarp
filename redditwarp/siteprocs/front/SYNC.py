
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_SYNC import LooseComment

from .pull_SYNC import Pull

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.listing.comment_listing_paginator import LooseCommentListingPaginator

class FrontProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.pull: Pull = Pull(client)

    def pull_new_comments(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[LooseCommentListingPaginator, LooseComment]:
        p = LooseCommentListingPaginator(self._client, '/comments')
        return ImpartedPaginatorChainingIterator(p, amount)
