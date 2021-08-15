
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Callable, Any, Iterable
if TYPE_CHECKING:
    from ....client_SYNC import Client

from .mixins.subreddit_detail_SYNC import SubredditDetail
from .user_pull_sync import SubmissionAndCommentListingPaginator, SubmissionListingPaginator
from ....models.submission_SYNC import Submission
from .listing_paginator import ListingPaginator

T = TypeVar('T')

class ArticleTypeFilter(ListingPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(client, uri, limit=limit, cursor_extractor=cursor_extractor)
        self.only = ''

    def _generate_params(self) -> Iterable[tuple[str, Optional[str]]]:
        yield from super()._generate_params()
        if self.only:
            yield ('only', self.only)


class ModQueueListingPaginator(
    ArticleTypeFilter[object],
    SubredditDetail[object],
    SubmissionAndCommentListingPaginator,
): pass

class ReportsListingPaginator(
    ArticleTypeFilter[object],
    SubredditDetail[object],
    SubmissionAndCommentListingPaginator,
): pass

class SpamListingPaginator(
    ArticleTypeFilter[object],
    SubredditDetail[object],
    SubmissionAndCommentListingPaginator,
): pass

class EditedListingPaginator(
    ArticleTypeFilter[object],
    SubredditDetail[object],
    SubmissionAndCommentListingPaginator,
): pass

class UnmoderatedListingPaginator(
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass
