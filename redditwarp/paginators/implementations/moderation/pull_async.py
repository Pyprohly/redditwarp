
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Iterable, Callable, Any
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ...listing.listing_async_paginator import ListingAsyncPaginator
from ...listing.mixins.subreddit_detail_ASYNC import SubredditDetail
from ...listing.submission_and_comment_listing_async_paginator import SubmissionAndExtraSubmissionFieldsCommentListingAsyncPaginator
from ...listing.submission_listing_async_paginator import SubmissionListingAsyncPaginator
from ...listing.comment_listing_async_paginator import ExtraSubmissionFieldsCommentListingAsyncPaginator
from ....models.submission_ASYNC import Submission
from ....models.comment_ASYNC import Comment

T = TypeVar('T')

class OnlyFilter(ListingAsyncPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(client, uri, limit=limit, cursor_extractor=cursor_extractor)
        self._only = ''

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        if self._only:
            yield ('only', self._only)

class SubmissionOnlyFilter(OnlyFilter[Submission]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(client, uri, limit=limit, cursor_extractor=cursor_extractor)
        self._only = 'links'

class CommentOnlyFilter(OnlyFilter[Comment]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(client, uri, limit=limit, cursor_extractor=cursor_extractor)
        self._only = 'comments'


class ModQueueListingAsyncPaginator(
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingAsyncPaginator,
): pass
class ModQueueSubmissionListingAsyncPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingAsyncPaginator,
): pass
class ModQueueCommentListingAsyncPaginator(
    SubredditDetail[Comment],
    CommentOnlyFilter,
    ExtraSubmissionFieldsCommentListingAsyncPaginator,
): pass

class ReportsListingAsyncPaginator(
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingAsyncPaginator,
): pass
class ReportsSubmissionListingAsyncPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingAsyncPaginator,
): pass
class ReportsCommentListingAsyncPaginator(
    SubredditDetail[Comment],
    CommentOnlyFilter,
    ExtraSubmissionFieldsCommentListingAsyncPaginator,
): pass

class SpamListingAsyncPaginator(
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingAsyncPaginator,
): pass
class SpamSubmissionListingAsyncPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingAsyncPaginator,
): pass
class SpamCommentListingAsyncPaginator(
    SubredditDetail[Comment],
    CommentOnlyFilter,
    ExtraSubmissionFieldsCommentListingAsyncPaginator,
): pass

class EditedListingAsyncPaginator(
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingAsyncPaginator,
): pass
class EditedSubmissionListingAsyncPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingAsyncPaginator,
): pass
class EditedCommentListingAsyncPaginator(
    SubredditDetail[Comment],
    CommentOnlyFilter,
    ExtraSubmissionFieldsCommentListingAsyncPaginator,
): pass

class UnmoderatedSubmissionListingAsyncPaginator(
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass
