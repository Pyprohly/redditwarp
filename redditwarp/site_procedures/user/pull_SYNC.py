
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_SYNC import ExtraSubmissionFieldsComment
    from ...models.submission_SYNC import Submission

from ...iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...iterators.paginators.listing.user_pull_sync import (
    OverviewListingPaginator,
    CommentsListingPaginator,
    SubmittedListingPaginator,
    GildedListingPaginator,
    UpvotedListingPaginator,
    DownvotedListingPaginator,
    HiddenListingPaginator,
    SavedListingPaginator,
)

class Pull:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[OverviewListingPaginator, object]:
        return self.overview(name, amount)

    def overview(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'new', time_filter: str = '',
            ) -> PaginatorChainingIterator[OverviewListingPaginator, object]:
        p = OverviewListingPaginator(self._client, f'/user/{name}/overview')
        p.sort = sort
        p.time_filter = time_filter
        return PaginatorChainingIterator(p, amount)

    def comments(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'new', time_filter: str = '',
            ) -> PaginatorChainingIterator[CommentsListingPaginator, ExtraSubmissionFieldsComment]:
        p = CommentsListingPaginator(self._client, f'/user/{name}/comments')
        p.sort = sort
        p.time_filter = time_filter
        return PaginatorChainingIterator(p, amount)

    def submitted(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'hot', time_filter: str = '',
            ) -> PaginatorChainingIterator[SubmittedListingPaginator, Submission]:
        p = SubmittedListingPaginator(self._client, f'/user/{name}/submitted')
        p.sort = sort
        p.time_filter = time_filter
        return PaginatorChainingIterator(p, amount)

    def awards_received(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[GildedListingPaginator, object]:
        p = GildedListingPaginator(self._client, f'/user/{name}/gilded')
        return PaginatorChainingIterator(p, amount)

    def awards_given(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[GildedListingPaginator, object]:
        p = GildedListingPaginator(self._client, f'/user/{name}/gilded/given')
        return PaginatorChainingIterator(p, amount)

    def upvoted(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[UpvotedListingPaginator, Submission]:
        p = UpvotedListingPaginator(self._client, f'/user/{name}/upvoted')
        return PaginatorChainingIterator(p, amount)

    def downvoted(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[DownvotedListingPaginator, Submission]:
        p = DownvotedListingPaginator(self._client, f'/user/{name}/downvoted')
        return PaginatorChainingIterator(p, amount)

    def hidden(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[HiddenListingPaginator, Submission]:
        p = HiddenListingPaginator(self._client, f'/user/{name}/hidden')
        return PaginatorChainingIterator(p, amount)

    def saved(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[SavedListingPaginator, object]:
        p = SavedListingPaginator(self._client, f'/user/{name}/saved')
        return PaginatorChainingIterator(p, amount)
