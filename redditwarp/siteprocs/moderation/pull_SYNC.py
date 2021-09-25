
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission
    from ...models.comment_SYNC import Comment

from functools import cached_property

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator, PaginatorChainingWrapper
from ...paginators.implementations.listing.p_moderation_pull_sync import (
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
                ) -> PaginatorChainingWrapper[ModQueueListingPaginator, object]:
            p = ModQueueListingPaginator(self._client, f'/r/{sr}/about/modqueue')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[ModQueueSubmissionListingPaginator, Submission]:
            p = ModQueueSubmissionListingPaginator(self._client, f'/r/{sr}/about/modqueue')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[ModQueueCommentListingPaginator, Comment]:
            p = ModQueueCommentListingPaginator(self._client, f'/r/{sr}/about/modqueue')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    modqueue = cached_property(_modqueue)

    class _reports:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[ReportsListingPaginator, object]:
            p = ReportsListingPaginator(self._client, f'/r/{sr}/about/reports')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[ReportsSubmissionListingPaginator, Submission]:
            p = ReportsSubmissionListingPaginator(self._client, f'/r/{sr}/about/reports')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[ReportsCommentListingPaginator, Comment]:
            p = ReportsCommentListingPaginator(self._client, f'/r/{sr}/about/reports')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    reports = cached_property(_reports)

    class _spam:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[SpamListingPaginator, object]:
            p = SpamListingPaginator(self._client, f'/r/{sr}/about/spam')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[SpamSubmissionListingPaginator, Submission]:
            p = SpamSubmissionListingPaginator(self._client, f'/r/{sr}/about/spam')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[SpamCommentListingPaginator, Comment]:
            p = SpamCommentListingPaginator(self._client, f'/r/{sr}/about/spam')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    spam = cached_property(_spam)

    class _edited:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[EditedListingPaginator, object]:
            p = EditedListingPaginator(self._client, f'/r/{sr}/about/edited')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[EditedSubmissionListingPaginator, Submission]:
            p = EditedSubmissionListingPaginator(self._client, f'/r/{sr}/about/edited')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> PaginatorChainingWrapper[EditedCommentListingPaginator, Comment]:
            p = EditedCommentListingPaginator(self._client, f'/r/{sr}/about/edited')
            return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    edited = cached_property(_edited)

    def unmoderated(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[UnmoderatedSubmissionListingPaginator, Submission]:
        p = UnmoderatedSubmissionListingPaginator(self._client, f'/r/{sr}/about/unmoderated')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)
