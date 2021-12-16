
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_SYNC import ExtraSubmissionFieldsComment
    from ...models.submission_SYNC import Submission

from functools import cached_property

from ...paginators.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...paginators.implementations.user._sync_ import (
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
            ) -> ImpartedPaginatorChainingIterator[OverviewListingPaginator, object]:
        return self.overview(name, amount)

    def overview(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'new',
            ) -> ImpartedPaginatorChainingIterator[OverviewListingPaginator, object]:
        p = OverviewListingPaginator(self._client, f'/user/{name}/overview')
        p.sort = sort
        return ImpartedPaginatorChainingIterator(p, amount)

    def comments(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'new',
            ) -> ImpartedPaginatorChainingIterator[CommentsListingPaginator, ExtraSubmissionFieldsComment]:
        p = CommentsListingPaginator(self._client, f'/user/{name}/comments')
        p.sort = sort
        return ImpartedPaginatorChainingIterator(p, amount)

    def submitted(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'hot',
            ) -> ImpartedPaginatorChainingIterator[SubmittedListingPaginator, Submission]:
        p = SubmittedListingPaginator(self._client, f'/user/{name}/submitted')
        p.sort = sort
        return ImpartedPaginatorChainingIterator(p, amount)

    def awards_received(self, name: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[GildedListingPaginator, object]:
        p = GildedListingPaginator(self._client, f'/user/{name}/gilded')
        return ImpartedPaginatorChainingIterator(p, amount)

    def awards_given(self, name: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[GildedListingPaginator, object]:
        p = GildedListingPaginator(self._client, f'/user/{name}/gilded/given')
        return ImpartedPaginatorChainingIterator(p, amount)

    def upvoted(self, name: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[UpvotedListingPaginator, Submission]:
        p = UpvotedListingPaginator(self._client, f'/user/{name}/upvoted')
        return ImpartedPaginatorChainingIterator(p, amount)

    def downvoted(self, name: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[DownvotedListingPaginator, Submission]:
        p = DownvotedListingPaginator(self._client, f'/user/{name}/downvoted')
        return ImpartedPaginatorChainingIterator(p, amount)

    def hidden(self, name: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[HiddenListingPaginator, Submission]:
        p = HiddenListingPaginator(self._client, f'/user/{name}/hidden')
        return ImpartedPaginatorChainingIterator(p, amount)

    class _saved:
        def __init__(self, outer: Pull) -> None:
            self._client = outer._client

        def __call__(self, name: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[SavedListingPaginator, object]:
            p = SavedListingPaginator(self._client, f'/user/{name}/saved')
            return ImpartedPaginatorChainingIterator(p, amount)

        def submissions(self, name: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[SavedSubmissionsListingPaginator, Submission]:
            p = SavedSubmissionsListingPaginator(self._client, f'/user/{name}/saved')
            return ImpartedPaginatorChainingIterator(p, amount)

        def comments(self, name: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[SavedCommentsListingPaginator, ExtraSubmissionFieldsComment]:
            p = SavedCommentsListingPaginator(self._client, f'/user/{name}/saved')
            return ImpartedPaginatorChainingIterator(p, amount)

    saved: cached_property[_saved] = cached_property(_saved)
