
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.comment_SYNC import NewComment

from .fetch_SYNC import Fetch
from .get_SYNC import Get
from .bulk_fetch_SYNC import BulkFetch
from .pull_SYNC import Pull
from .take_SYNC import Take

from ....iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ....iterators.paginators.listing.comment_listing_paginator import CommentListingPaginator

class Subreddit:
    def __init__(self, client: Client):
        self._client = client
        self.get = Get(client)
        self.fetch = Fetch(client)
        self.bulk_fetch = BulkFetch(client)
        self.pull = Pull(client)
        self.take = Take(client)

    def pull_comments(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[CommentListingPaginator, NewComment]:
        p = CommentListingPaginator(self._client, f'/r/{sr}/comments')
        return PaginatorChainingIterator(p, amount)
