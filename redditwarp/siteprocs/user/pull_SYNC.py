
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_SYNC import ExtraSubmissionFieldsComment
    from ...models.submission_SYNC import Submission

from functools import cached_property

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator, PaginatorChainingWrapper
from ...paginators.implementations.listing.p_user_pull_sync import (
    OverviewListingPaginator,
    CommentsListingPaginator,
    SubmittedListingPaginator,
    GildedListingPaginator,
    UpvotedListingPaginator,
    DownvotedListingPaginator,
    HiddenListingPaginator,
    SavedListingPaginator,
    SavedSubmissionsListingPaginator,
    SavedCommentsListingPaginator,
)

class Pull:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[OverviewListingPaginator, object]:
        return self.overview(name, amount)

    def overview(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'new',
            ) -> PaginatorChainingWrapper[OverviewListingPaginator, object]:
        p = OverviewListingPaginator(self._client, f'/user/{name}/overview')
        p.sort = sort
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def comments(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'new',
            ) -> PaginatorChainingWrapper[CommentsListingPaginator, ExtraSubmissionFieldsComment]:
        p = CommentsListingPaginator(self._client, f'/user/{name}/comments')
        p.sort = sort
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def submitted(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'hot',
            ) -> PaginatorChainingWrapper[SubmittedListingPaginator, Submission]:
        p = SubmittedListingPaginator(self._client, f'/user/{name}/submitted')
        p.sort = sort
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def awards_received(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[GildedListingPaginator, object]:
        p = GildedListingPaginator(self._client, f'/user/{name}/gilded')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def awards_given(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[GildedListingPaginator, object]:
        p = GildedListingPaginator(self._client, f'/user/{name}/gilded/given')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def upvoted(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[UpvotedListingPaginator, Submission]:
        p = UpvotedListingPaginator(self._client, f'/user/{name}/upvoted')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def downvoted(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[DownvotedListingPaginator, Submission]:
        p = DownvotedListingPaginator(self._client, f'/user/{name}/downvoted')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def hidden(self, name: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[HiddenListingPaginator, Submission]:
        p = HiddenListingPaginator(self._client, f'/user/{name}/hidden')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    class _saved:
        def __init__(self, outer: Pull) -> None:
            self._client = outer._client

        def __call__(self, name: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[SavedListingPaginator, object]:
            p = SavedListingPaginator(self._client, f'/user/{name}/saved')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

        def submissions(self, name: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[SavedSubmissionsListingPaginator, Submission]:
            p = SavedSubmissionsListingPaginator(self._client, f'/user/{name}/saved')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

        def comments(self, name: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[SavedCommentsListingPaginator, ExtraSubmissionFieldsComment]:
            p = SavedCommentsListingPaginator(self._client, f'/user/{name}/saved')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    saved: cached_property[_saved] = cached_property(_saved)
