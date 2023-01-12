
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Iterable, Callable, Any, Mapping
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ..listing.listing_paginator import ListingPaginator
from ..listing.mixins.subreddit_detail_SYNC import SubredditDetail
from ..listing.submission_and_comment_listing_paginator import SubmissionAndLooseCommentListingPaginator
from ..listing.submission_listing_paginator import SubmissionListingPaginator
from ..listing.comment_listing_paginator import LooseCommentListingPaginator
from ....models.submission_SYNC import Submission
from ....models.comment_SYNC import LooseComment

T = TypeVar('T')

class OnlyFilter(ListingPaginator[T]):
    def __init__(self,
        client: Client,
        url: str,
        *,
        limit: Optional[int] = 100,
        params: Optional[Mapping[str, str]] = None,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ) -> None:
        super().__init__(client, url, limit=limit, params=params, cursor_extractor=cursor_extractor)
        self._only = ''

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        if self._only:
            yield ('only', self._only)

class SubmissionOnlyFilter(OnlyFilter[Submission]):
    def __init__(self,
        client: Client,
        url: str,
        *,
        limit: Optional[int] = 100,
        params: Optional[Mapping[str, str]] = None,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ) -> None:
        super().__init__(client, url, limit=limit, params=params, cursor_extractor=cursor_extractor)
        self._only = 'links'

class CommentOnlyFilter(OnlyFilter[LooseComment]):
    def __init__(self,
        client: Client,
        url: str,
        *,
        limit: Optional[int] = 100,
        params: Optional[Mapping[str, str]] = None,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ) -> None:
        super().__init__(client, url, limit=limit, params=params, cursor_extractor=cursor_extractor)
        self._only = 'comments'


class ModQueueListingPaginator(
    SubredditDetail[object],
    SubmissionAndLooseCommentListingPaginator,
): pass
class ModQueueSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingPaginator,
): pass
class ModQueueCommentListingPaginator(
    SubredditDetail[LooseComment],
    CommentOnlyFilter,
    LooseCommentListingPaginator,
): pass

class ReportsListingPaginator(
    SubredditDetail[object],
    SubmissionAndLooseCommentListingPaginator,
): pass
class ReportsSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingPaginator,
): pass
class ReportsCommentListingPaginator(
    SubredditDetail[LooseComment],
    CommentOnlyFilter,
    LooseCommentListingPaginator,
): pass

class SpamListingPaginator(
    SubredditDetail[object],
    SubmissionAndLooseCommentListingPaginator,
): pass
class SpamSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingPaginator,
): pass
class SpamCommentListingPaginator(
    SubredditDetail[LooseComment],
    CommentOnlyFilter,
    LooseCommentListingPaginator,
): pass

class EditedListingPaginator(
    SubredditDetail[object],
    SubmissionAndLooseCommentListingPaginator,
): pass
class EditedSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionOnlyFilter,
    SubmissionListingPaginator,
): pass
class EditedCommentListingPaginator(
    SubredditDetail[LooseComment],
    CommentOnlyFilter,
    LooseCommentListingPaginator,
): pass

class UnmoderatedSubmissionListingPaginator(
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass
