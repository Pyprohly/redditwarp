
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.comment_ASYNC import LooseComment

from .pull_ASYNC import Pull

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.listing.comment_listing_async_paginator import LooseCommentListingAsyncPaginator

class FrontProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.pull: Pull = Pull(client)

    def pull_new_comments(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[LooseCommentListingAsyncPaginator, LooseComment]:
        p = LooseCommentListingAsyncPaginator(self._client, '/comments')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
