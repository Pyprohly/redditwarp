
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_ASYNC import Submission
    from ...models.comment_ASYNC import Comment

from functools import cached_property

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.moderation.async1 import (
    ModQueueListingAsyncPaginator,
    ModQueueSubmissionListingAsyncPaginator,
    ModQueueCommentListingAsyncPaginator,
    ReportsListingAsyncPaginator,
    ReportsSubmissionListingAsyncPaginator,
    ReportsCommentListingAsyncPaginator,
    SpamListingAsyncPaginator,
    SpamSubmissionListingAsyncPaginator,
    SpamCommentListingAsyncPaginator,
    EditedListingAsyncPaginator,
    EditedSubmissionListingAsyncPaginator,
    EditedCommentListingAsyncPaginator,
    UnmoderatedSubmissionListingAsyncPaginator,
)

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    class ModQueue:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[ModQueueListingAsyncPaginator, object]:
            p = ModQueueListingAsyncPaginator(self._client, f'/r/{sr}/about/modqueue')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[ModQueueSubmissionListingAsyncPaginator, Submission]:
            p = ModQueueSubmissionListingAsyncPaginator(self._client, f'/r/{sr}/about/modqueue')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[ModQueueCommentListingAsyncPaginator, Comment]:
            p = ModQueueCommentListingAsyncPaginator(self._client, f'/r/{sr}/about/modqueue')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

    modqueue: cached_property[ModQueue] = cached_property(ModQueue)
    ("""
        Retrieve submissions/comments relevant to moderators.

        .. .PARAMETERS

        :param `str` sr:
        :param `Optional[int]` amount:

        .. .RETURNS

        :returns:
            A paginator iterator of either :class:`~.models.submission_ASYNC.Submission`
            or :class:`~.models.comment_ASYNC.Comment` objects.
        :rtype: :class:`~.pagination.paginator_chaining_async_iterator.ImpartedPaginatorChainingAsyncIterator`\\[:class:`~.pagination.paginators.moderation.async1.ModQueueListingAsyncPaginator`, `object`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - You don't have access to the subreddit.
               - You don't have the 'posts' moderator permission.
            + `403`:
                The specified subreddit name is too long (over 21 characters)
                or contains invalid characters.
        """)

    class Reported:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[ReportsListingAsyncPaginator, object]:
            p = ReportsListingAsyncPaginator(self._client, f'/r/{sr}/about/reports')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[ReportsSubmissionListingAsyncPaginator, Submission]:
            p = ReportsSubmissionListingAsyncPaginator(self._client, f'/r/{sr}/about/reports')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[ReportsCommentListingAsyncPaginator, Comment]:
            p = ReportsCommentListingAsyncPaginator(self._client, f'/r/{sr}/about/reports')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

    reported: cached_property[Reported] = cached_property(Reported)
    ("""
        Behaves similarly to :meth:`.modqueue`.
        """)

    class Spam:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[SpamListingAsyncPaginator, object]:
            p = SpamListingAsyncPaginator(self._client, f'/r/{sr}/about/spam')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[SpamSubmissionListingAsyncPaginator, Submission]:
            p = SpamSubmissionListingAsyncPaginator(self._client, f'/r/{sr}/about/spam')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[SpamCommentListingAsyncPaginator, Comment]:
            p = SpamCommentListingAsyncPaginator(self._client, f'/r/{sr}/about/spam')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

    spam: cached_property[Spam] = cached_property(Spam)
    ("""
        Behaves similarly to :meth:`.modqueue`.
        """)

    class Edited:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[EditedListingAsyncPaginator, object]:
            p = EditedListingAsyncPaginator(self._client, f'/r/{sr}/about/edited')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[EditedSubmissionListingAsyncPaginator, Submission]:
            p = EditedSubmissionListingAsyncPaginator(self._client, f'/r/{sr}/about/edited')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[EditedCommentListingAsyncPaginator, Comment]:
            p = EditedCommentListingAsyncPaginator(self._client, f'/r/{sr}/about/edited')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

    edited: cached_property[Edited] = cached_property(Edited)
    ("""
        Behaves similarly to :meth:`.modqueue`.
        """)

    def unmoderated(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[UnmoderatedSubmissionListingAsyncPaginator, Submission]:
        """
        Behaves similarly to :meth:`.modqueue`.
        """
        p = UnmoderatedSubmissionListingAsyncPaginator(self._client, f'/r/{sr}/about/unmoderated')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
