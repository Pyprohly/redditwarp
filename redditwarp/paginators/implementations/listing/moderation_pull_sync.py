
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Callable, Any, Iterable
if TYPE_CHECKING:
    from ....client_SYNC import Client

from .mixins.subreddit_detail_SYNC import SubredditDetail
from .user_pull_sync import SubmissionAndCommentListingPaginator, SubmissionListingPaginator, CommentListingPaginator
from ....models.submission_SYNC import Submission
from ....models.comment_SYNC import Comment
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
        self._only = ''

    def _generate_params(self) -> Iterable[tuple[str, Optional[str]]]:
        yield from super()._generate_params()
        if self._only:
            yield ('only', self._only)

class SubmissionArticleTypeFilter(ArticleTypeFilter[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(client, uri, limit=limit, cursor_extractor=cursor_extractor)
        self._only = 'links'

class CommentArticleTypeFilter(ArticleTypeFilter[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(client, uri, limit=limit, cursor_extractor=cursor_extractor)
        self._only = 'comments'


class ModQueueListingPaginator(
    SubredditDetail[object],
    SubmissionAndCommentListingPaginator,
): pass
class ModQueueSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionArticleTypeFilter[Submission],
    SubmissionListingPaginator,
): pass
class ModQueueCommentListingPaginator(
    SubredditDetail[Comment],
    CommentArticleTypeFilter[Comment],
    CommentListingPaginator,
): pass

class ReportsListingPaginator(
    SubredditDetail[object],
    SubmissionAndCommentListingPaginator,
): pass
class ReportsSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionArticleTypeFilter[Submission],
    SubmissionListingPaginator,
): pass
class ReportsCommentListingPaginator(
    SubredditDetail[Comment],
    CommentArticleTypeFilter[Comment],
    CommentListingPaginator,
): pass

class SpamListingPaginator(
    SubredditDetail[object],
    SubmissionAndCommentListingPaginator,
): pass
class SpamSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionArticleTypeFilter[Submission],
    SubmissionListingPaginator,
): pass
class SpamCommentListingPaginator(
    SubredditDetail[Comment],
    CommentArticleTypeFilter[Comment],
    CommentListingPaginator,
): pass

class EditedListingPaginator(
    SubredditDetail[object],
    SubmissionAndCommentListingPaginator,
): pass
class EditedSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionArticleTypeFilter[Submission],
    SubmissionListingPaginator,
): pass
class EditedCommentListingPaginator(
    SubredditDetail[Comment],
    CommentArticleTypeFilter[Comment],
    CommentListingPaginator,
): pass

class UnmoderatedSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass
