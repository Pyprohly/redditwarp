
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit as SubredditModel
    from ...models.comment_SYNC import NewComment

from ...models.load.subreddit_SYNC import load_subreddit
from .fetch_SYNC import Fetch
from .get_SYNC import Get
from .pull_SYNC import Pull
from .grab_SYNC import Grab

from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk_SYNC import CallChunk
from ...iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...iterators.paginators.listing.comment_listing_paginator import CommentListingPaginator

class Subreddit:
    def __init__(self, client: Client):
        self._client = client
        self.get = Get(client)
        self.fetch = Fetch(client)
        self.pull = Pull(client)
        self.grab = Grab(client)

    def bulk_fetch(self, ids: Iterable[int]) -> CallChunkChainingIterator[int, SubredditModel]:
        def mass_fetch(ids: Sequence[int]) -> Sequence[SubredditModel]:
            id36s = map(to_base36, ids)
            full_id36s = map('t5_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_subreddit(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingIterator(
                CallChunk(mass_fetch, idfs) for idfs in chunked(ids, 100))

    def pull_new_comments(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[CommentListingPaginator, NewComment]:
        p = CommentListingPaginator(self._client, f'/r/{sr}/comments')
        return PaginatorChainingIterator(p, amount)

    def submit(self) -> None:
        ...

    def subscribe(self) -> None:
        ...
