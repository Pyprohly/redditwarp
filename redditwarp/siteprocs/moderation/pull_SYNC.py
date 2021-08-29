
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission
    from ...models.comment_SYNC import Comment

from functools import cached_property

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...paginators.implementations.listing.moderation_pull_sync import (
    ModQueueListingPaginator,
    ModQueueSubmissionListingPaginator,
    ModQueueCommentListingPaginator,
    ReportsListingPaginator,
    ReportsSubmissionListingPaginator,
    ReportsCommentListingPaginator,
    SpamListingPaginator,
    SpamSubmissionListingPaginator,
    SpamCommentListingPaginator,
    EditedListingPaginator,
    EditedSubmissionListingPaginator,
    EditedCommentListingPaginator,
    UnmoderatedSubmissionListingPaginator,
)

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    class _modqueue:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[ModQueueListingPaginator, object]:
            p = ModQueueListingPaginator(self._client, f'/r/{sr}/about/modqueue')
            return PaginatorChainingIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[ModQueueSubmissionListingPaginator, Submission]:
            p = ModQueueSubmissionListingPaginator(self._client, f'/r/{sr}/about/modqueue')
            return PaginatorChainingIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[ModQueueCommentListingPaginator, Comment]:
            p = ModQueueCommentListingPaginator(self._client, f'/r/{sr}/about/modqueue')
            return PaginatorChainingIterator(p, amount)

    modqueue = cached_property(_modqueue)

    class _reports:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[ReportsListingPaginator, object]:
            p = ReportsListingPaginator(self._client, f'/r/{sr}/about/reports')
            return PaginatorChainingIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[ReportsSubmissionListingPaginator, Submission]:
            p = ReportsSubmissionListingPaginator(self._client, f'/r/{sr}/about/reports')
            return PaginatorChainingIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[ReportsCommentListingPaginator, Comment]:
            p = ReportsCommentListingPaginator(self._client, f'/r/{sr}/about/reports')
            return PaginatorChainingIterator(p, amount)

    reports = cached_property(_reports)

    class _spam:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[SpamListingPaginator, object]:
            p = SpamListingPaginator(self._client, f'/r/{sr}/about/spam')
            return PaginatorChainingIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[SpamSubmissionListingPaginator, Submission]:
            p = SpamSubmissionListingPaginator(self._client, f'/r/{sr}/about/spam')
            return PaginatorChainingIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[SpamCommentListingPaginator, Comment]:
            p = SpamCommentListingPaginator(self._client, f'/r/{sr}/about/spam')
            return PaginatorChainingIterator(p, amount)

    spam = cached_property(_spam)

    class _edited:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[EditedListingPaginator, object]:
            p = EditedListingPaginator(self._client, f'/r/{sr}/about/edited')
            return PaginatorChainingIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[EditedSubmissionListingPaginator, Submission]:
            p = EditedSubmissionListingPaginator(self._client, f'/r/{sr}/about/edited')
            return PaginatorChainingIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingIterator[EditedCommentListingPaginator, Comment]:
            p = EditedCommentListingPaginator(self._client, f'/r/{sr}/about/edited')
            return PaginatorChainingIterator(p, amount)

    edited = cached_property(_edited)

    def unmoderated(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[UnmoderatedSubmissionListingPaginator, Submission]:
        p = UnmoderatedSubmissionListingPaginator(self._client, f'/r/{sr}/about/unmoderated')
        return PaginatorChainingIterator(p, amount)
