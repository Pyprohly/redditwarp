
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_ASYNC import Submission
    from ...models.comment_ASYNC import Comment

from functools import cached_property

from ...paginators.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...paginators.implementations.moderation._async_ import (
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

    class _modqueue:
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

    modqueue: cached_property[_modqueue] = cached_property(_modqueue)

    class _reports:
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

    reports: cached_property[_reports] = cached_property(_reports)

    class _spam:
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

    spam: cached_property[_spam] = cached_property(_spam)

    class _edited:
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

    edited: cached_property[_edited] = cached_property(_edited)

    def unmoderated(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[UnmoderatedSubmissionListingAsyncPaginator, Submission]:
        p = UnmoderatedSubmissionListingAsyncPaginator(self._client, f'/r/{sr}/about/unmoderated')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
