
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Iterable, Callable, Any
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ..listing.listing_paginator import ListingPaginator
from ..listing.mixins.subreddit_detail_SYNC import SubredditDetail
from ..listing.submission_and_comment_listing_paginator import SubmissionAndExtraSubmissionFieldsCommentListingPaginator
from ..listing.submission_listing_paginator import SubmissionListingPaginator
from ..listing.comment_listing_paginator import ExtraSubmissionFieldsCommentListingPaginator
from ....models.submission_SYNC import Submission
from ....models.comment_SYNC import Comment

T = TypeVar('T')

class OnlyFilter(ListingPaginator[T]):
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


class ModQueueListingPaginator(
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingPaginator,
): pass
class ModQueueSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingPaginator,
): pass
class ModQueueCommentListingPaginator(
    SubredditDetail[Comment],
    CommentOnlyFilter,
    ExtraSubmissionFieldsCommentListingPaginator,
): pass

class ReportsListingPaginator(
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingPaginator,
): pass
class ReportsSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingPaginator,
): pass
class ReportsCommentListingPaginator(
    SubredditDetail[Comment],
    CommentOnlyFilter,
    ExtraSubmissionFieldsCommentListingPaginator,
): pass

class SpamListingPaginator(
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingPaginator,
): pass
class SpamSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingPaginator,
): pass
class SpamCommentListingPaginator(
    SubredditDetail[Comment],
    CommentOnlyFilter,
    ExtraSubmissionFieldsCommentListingPaginator,
): pass

class EditedListingPaginator(
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingPaginator,
): pass
class EditedSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingPaginator,
): pass
class EditedCommentListingPaginator(
    SubredditDetail[Comment],
    CommentOnlyFilter,
    ExtraSubmissionFieldsCommentListingPaginator,
): pass

class UnmoderatedSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass
