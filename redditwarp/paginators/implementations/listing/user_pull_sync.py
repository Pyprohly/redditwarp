
from __future__ import annotations
from typing import Sequence, Optional

from .mixins.sort_SYNC import Sort
from .mixins.time_filter_SYNC import TimeFilter
from .mixins.subreddit_detail_SYNC import SubredditDetail
from .listing_paginator import ListingPaginator
from ....models.comment_SYNC import ExtraSubmissionFieldsComment
from ....models.load.comment_SYNC import load_extra_submission_fields_comment
from ....models.load.submission_SYNC import load_submission
from ....models.submission_SYNC import Submission


class SubmissionAndCommentListingPaginator(ListingPaginator[object]):
    def next_result(self) -> Sequence[object]:
        data = self._fetch_data()
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

class CommentListingPaginator(ListingPaginator[ExtraSubmissionFieldsComment]):
    def next_result(self) -> Sequence[ExtraSubmissionFieldsComment]:
        data = self._fetch_data()
        return [load_extra_submission_fields_comment(d['data'], self.client) for d in data['children']]

class SubmissionListingPaginator(ListingPaginator[Submission]):
    def next_result(self) -> Sequence[Submission]:
        data = self._fetch_data()
        return [load_submission(d['data'], self.client) for d in data['children']]


class OverviewListingPaginator(
    Sort[object],
    TimeFilter[object],
    SubredditDetail[object],
    SubmissionAndCommentListingPaginator,
): pass

class CommentsListingPaginator(
    Sort[ExtraSubmissionFieldsComment],
    TimeFilter[ExtraSubmissionFieldsComment],
    SubredditDetail[ExtraSubmissionFieldsComment],
    CommentListingPaginator,
): pass

class SubmittedListingPaginator(
    Sort[Submission],
    TimeFilter[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class GildedListingPaginator(
    Sort[object],
    TimeFilter[object],
    SubredditDetail[object],
    SubmissionAndCommentListingPaginator,
): pass

class UpvotedListingPaginator(
    Sort[Submission],
    TimeFilter[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class DownvotedListingPaginator(
    Sort[Submission],
    TimeFilter[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class HiddenListingPaginator(
    Sort[Submission],
    TimeFilter[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class SavedListingPaginator(
    Sort[object],
    TimeFilter[object],
    SubredditDetail[object],
    SubmissionAndCommentListingPaginator,
): pass
