
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission
    from ...models.comment_SYNC import Comment

from functools import cached_property

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.moderation.sync1 import (
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

    class ModQueue:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[ModQueueListingPaginator, object]:
            p = ModQueueListingPaginator(self._client, f'/r/{sr}/about/modqueue')
            return ImpartedPaginatorChainingIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[ModQueueSubmissionListingPaginator, Submission]:
            p = ModQueueSubmissionListingPaginator(self._client, f'/r/{sr}/about/modqueue')
            return ImpartedPaginatorChainingIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[ModQueueCommentListingPaginator, Comment]:
            p = ModQueueCommentListingPaginator(self._client, f'/r/{sr}/about/modqueue')
            return ImpartedPaginatorChainingIterator(p, amount)

    modqueue: cached_property[ModQueue] = cached_property(ModQueue)

    class Reported:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[ReportsListingPaginator, object]:
            p = ReportsListingPaginator(self._client, f'/r/{sr}/about/reports')
            return ImpartedPaginatorChainingIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[ReportsSubmissionListingPaginator, Submission]:
            p = ReportsSubmissionListingPaginator(self._client, f'/r/{sr}/about/reports')
            return ImpartedPaginatorChainingIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[ReportsCommentListingPaginator, Comment]:
            p = ReportsCommentListingPaginator(self._client, f'/r/{sr}/about/reports')
            return ImpartedPaginatorChainingIterator(p, amount)

    reported: cached_property[Reported] = cached_property(Reported)

    class Spam:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[SpamListingPaginator, object]:
            p = SpamListingPaginator(self._client, f'/r/{sr}/about/spam')
            return ImpartedPaginatorChainingIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[SpamSubmissionListingPaginator, Submission]:
            p = SpamSubmissionListingPaginator(self._client, f'/r/{sr}/about/spam')
            return ImpartedPaginatorChainingIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[SpamCommentListingPaginator, Comment]:
            p = SpamCommentListingPaginator(self._client, f'/r/{sr}/about/spam')
            return ImpartedPaginatorChainingIterator(p, amount)

    spam: cached_property[Spam] = cached_property(Spam)

    class Edited:
        def __init__(self, outer: Pull) -> None:
            self._outer = outer
            self._client = outer._client

        def __call__(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[EditedListingPaginator, object]:
            p = EditedListingPaginator(self._client, f'/r/{sr}/about/edited')
            return ImpartedPaginatorChainingIterator(p, amount)

        def submissions(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[EditedSubmissionListingPaginator, Submission]:
            p = EditedSubmissionListingPaginator(self._client, f'/r/{sr}/about/edited')
            return ImpartedPaginatorChainingIterator(p, amount)

        def comments(self, sr: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[EditedCommentListingPaginator, Comment]:
            p = EditedCommentListingPaginator(self._client, f'/r/{sr}/about/edited')
            return ImpartedPaginatorChainingIterator(p, amount)

    edited: cached_property[Edited] = cached_property(Edited)

    def unmoderated(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[UnmoderatedSubmissionListingPaginator, Submission]:
        p = UnmoderatedSubmissionListingPaginator(self._client, f'/r/{sr}/about/unmoderated')
        return ImpartedPaginatorChainingIterator(p, amount)
