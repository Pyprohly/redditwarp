
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.comment_ASYNC import ExtraSubmissionFieldsComment
    from ...models.submission_ASYNC import Submission

from functools import cached_property

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.implementations.user.async_ import (
    OverviewListingAsyncPaginator,
    CommentsListingAsyncPaginator,
    SubmittedListingAsyncPaginator,
    GildedListingAsyncPaginator,
    UpvotedListingAsyncPaginator,
    DownvotedListingAsyncPaginator,
    HiddenListingAsyncPaginator,
    SavedListingAsyncPaginator,
    SavedSubmissionsListingAsyncPaginator,
    SavedCommentsListingAsyncPaginator,
)

class Pull:
    def __init__(self, client: Client):
        self._client = client

    def overview(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'new',
            ) -> ImpartedPaginatorChainingAsyncIterator[OverviewListingAsyncPaginator, object]:
        p = OverviewListingAsyncPaginator(self._client, f'/user/{name}/overview')
        p.sort = sort
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def comments(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'new',
            ) -> ImpartedPaginatorChainingAsyncIterator[CommentsListingAsyncPaginator, ExtraSubmissionFieldsComment]:
        p = CommentsListingAsyncPaginator(self._client, f'/user/{name}/comments')
        p.sort = sort
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def submitted(self, name: str, amount: Optional[int] = None, *,
            sort: str = 'hot',
            ) -> ImpartedPaginatorChainingAsyncIterator[SubmittedListingAsyncPaginator, Submission]:
        p = SubmittedListingAsyncPaginator(self._client, f'/user/{name}/submitted')
        p.sort = sort
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def awards_received(self, name: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[GildedListingAsyncPaginator, object]:
        p = GildedListingAsyncPaginator(self._client, f'/user/{name}/gilded')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def awards_given(self, name: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[GildedListingAsyncPaginator, object]:
        p = GildedListingAsyncPaginator(self._client, f'/user/{name}/gilded/given')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def upvoted(self, name: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[UpvotedListingAsyncPaginator, Submission]:
        p = UpvotedListingAsyncPaginator(self._client, f'/user/{name}/upvoted')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def downvoted(self, name: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[DownvotedListingAsyncPaginator, Submission]:
        p = DownvotedListingAsyncPaginator(self._client, f'/user/{name}/downvoted')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def hidden(self, name: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[HiddenListingAsyncPaginator, Submission]:
        p = HiddenListingAsyncPaginator(self._client, f'/user/{name}/hidden')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    class _saved:
        def __init__(self, outer: Pull) -> None:
            self._client = outer._client

        def __call__(self, name: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[SavedListingAsyncPaginator, object]:
            p = SavedListingAsyncPaginator(self._client, f'/user/{name}/saved')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def submissions(self, name: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[SavedSubmissionsListingAsyncPaginator, Submission]:
            p = SavedSubmissionsListingAsyncPaginator(self._client, f'/user/{name}/saved')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def comments(self, name: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[SavedCommentsListingAsyncPaginator, ExtraSubmissionFieldsComment]:
            p = SavedCommentsListingAsyncPaginator(self._client, f'/user/{name}/saved')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

    saved: cached_property[_saved] = cached_property(_saved)
