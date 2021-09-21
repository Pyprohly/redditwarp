
from __future__ import annotations
from typing import Sequence, Optional, Iterable

from .mixins.sort_SYNC import Sort
from .mixins.subreddit_detail_SYNC import SubredditDetail
from .listing_paginator import ListingPaginator
from .submission_listing_paginator_sync import SubmissionListingPaginator
from ....models.comment_SYNC import ExtraSubmissionFieldsComment
from ....models.load.comment_SYNC import load_extra_submission_fields_comment
from ....models.load.submission_SYNC import load_submission
from ....models.submission_SYNC import Submission

class SubmissionAndExtraSubmissionFieldsCommentListingPaginator(ListingPaginator[object]):
    def next_result(self) -> Sequence[object]:
        data = self._next_data()
        l = []
        for child in data['children']:
            kind = child['kind']
            data = child['data']
            obj: Optional[object] = None
            if kind == 't1':
                obj = load_extra_submission_fields_comment(data, self.client)
            elif kind == 't3':
                obj = load_submission(data, self.client)
            if obj is None:
                raise ValueError(f'unexpected kind {kind!r}')
            l.append(obj)
        return l

class ExtraSubmissionFieldsCommentListingPaginator(ListingPaginator[ExtraSubmissionFieldsComment]):
    def next_result(self) -> Sequence[ExtraSubmissionFieldsComment]:
        data = self._next_data()
        return [load_extra_submission_fields_comment(d['data'], self.client) for d in data['children']]


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
    Sort[object],
    SubredditDetail[object],
    SubmissionListingPaginator,
):
    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('type', 'links')

class SavedCommentsListingPaginator(
    Sort[object],
    SubredditDetail[object],
    ExtraSubmissionFieldsCommentListingPaginator,
):
    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('type', 'comments')
