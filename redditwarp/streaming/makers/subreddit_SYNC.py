
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission
    from ...models.comment_SYNC import LooseComment
    from ...models.subreddit_SYNC import Subreddit
    from ..stream_SYNC import IStandardStreamEventSubject
    from ...pagination.paginator import CursorPaginator

from ..stream_SYNC import Stream


def submission_stream_extractor(x: Submission) -> object:
    return x.id

def get_submission_stream_paginator(client: Client, sr: str) -> CursorPaginator[Submission]:
    return client.p.subreddit.pull.new(sr).get_paginator()

def make_submission_stream(paginator: CursorPaginator[Submission], past: Optional[Iterable[Submission]] = None, seen: Optional[Iterable[object]] = None) -> IStandardStreamEventSubject[Submission]:
    return Stream(paginator, submission_stream_extractor, past=past, seen=seen)

def create_submission_stream(client: Client, sr: str) -> IStandardStreamEventSubject[Submission]:
    return make_submission_stream(get_submission_stream_paginator(client, sr))


def comment_stream_extractor(x: LooseComment) -> object:
    return x.id

def get_comment_stream_paginator(client: Client, sr: str) -> CursorPaginator[LooseComment]:
    return client.p.subreddit.pull_new_comments(sr).get_paginator()

def make_comment_stream(paginator: CursorPaginator[LooseComment], past: Optional[Iterable[LooseComment]] = None, seen: Optional[Iterable[object]] = None) -> IStandardStreamEventSubject[LooseComment]:
    return Stream(paginator, comment_stream_extractor, past=past, seen=seen)

def create_comment_stream(client: Client, sr: str) -> IStandardStreamEventSubject[LooseComment]:
    return make_comment_stream(get_comment_stream_paginator(client, sr))


def subreddit_stream_extractor(x: Subreddit) -> object:
    return x.id

def get_subreddit_stream_paginator(client: Client) -> CursorPaginator[Subreddit]:
    return client.p.subreddit.pulls.new().get_paginator()

def make_subreddit_stream(paginator: CursorPaginator[Subreddit], past: Optional[Iterable[Subreddit]] = None, seen: Optional[Iterable[object]] = None) -> IStandardStreamEventSubject[Subreddit]:
    return Stream(paginator, subreddit_stream_extractor, past=past, seen=seen)

def create_subreddit_stream(client: Client) -> IStandardStreamEventSubject[Subreddit]:
    return make_subreddit_stream(get_subreddit_stream_paginator(client))
