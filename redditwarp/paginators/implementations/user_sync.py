
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..listing.mixins.sort_SYNC import Sort
from ..listing.listing_paginator import ListingPaginator
from ..listing.mixins.subreddit_detail_SYNC import SubredditDetail
from ..listing.submission_listing_paginator_sync import SubmissionListingPaginator
from ..listing.comment_listing_paginator_sync import ExtraSubmissionFieldsCommentListingPaginator
from ..listing.submission_and_comment_listing_paginator_sync import SubmissionAndExtraSubmissionFieldsCommentListingPaginator
from ...models.comment_SYNC import ExtraSubmissionFieldsComment
from ...models.submission_SYNC import Submission
from ..listing.subreddit_listing_paginator_sync import SubredditListingPaginator
from ...models.subreddit_SYNC import Subreddit
from ...models.user_SYNC import User
from ...models.load.user_SYNC import load_user


class SearchUsersListingPaginator(
    Sort[User],
    ListingPaginator[User],
):
    def __init__(self,
        client: Client,
        uri: str,
        query: str,
    ):
        super().__init__(client, uri)
        self.query: str = query

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('q', self.query)

    def fetch_next(self) -> Sequence[User]:
        data = self._fetch_next_data()
        return [load_user(d['data'], self.client) for d in data['children']]


###

class OverviewListingPaginator(
    Sort[object],
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingPaginator,
): pass

class CommentsListingPaginator(
    Sort[ExtraSubmissionFieldsComment],
    SubredditDetail[ExtraSubmissionFieldsComment],
    ExtraSubmissionFieldsCommentListingPaginator,
): pass

class SubmittedListingPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class GildedListingPaginator(
    Sort[object],
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingPaginator,
): pass

class UpvotedListingPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class DownvotedListingPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class HiddenListingPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class SavedListingPaginator(
    Sort[object],
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingPaginator,
): pass

class SavedSubmissionsListingPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
):
    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('type', 'links')

class SavedCommentsListingPaginator(
    Sort[ExtraSubmissionFieldsComment],
    SubredditDetail[ExtraSubmissionFieldsComment],
    ExtraSubmissionFieldsCommentListingPaginator,
):
    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('type', 'comments')


###

class UserSubredditListingPaginator(
    SubredditDetail[Subreddit],
    SubredditListingPaginator,
): pass
