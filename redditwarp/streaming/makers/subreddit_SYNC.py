
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission
    from ...models.comment_SYNC import LooseComment
    from ...models.subreddit_SYNC import Subreddit
    from ..stream_SYNC import IStandardStreamEventSubject
    from ...pagination.paginator import CursorPaginator

from ..stream_SYNC import Stream


def get_submission_stream_paginator(client: Client, sr: str) -> CursorPaginator[Submission]:
    return client.p.subreddit.pull.new(sr).get_paginator()

def make_submission_stream(paginator: CursorPaginator[Submission], seen: Iterable[Submission] = ()) -> IStandardStreamEventSubject[Submission]:
    return Stream(paginator, lambda x: x.id, seen)

def create_submission_stream(client: Client, sr: str) -> IStandardStreamEventSubject[Submission]:
    return make_submission_stream(get_submission_stream_paginator(client, sr))


def get_comment_stream_paginator(client: Client, sr: str) -> CursorPaginator[LooseComment]:
    return client.p.subreddit.pull_new_comments(sr).get_paginator()

def make_comment_stream(paginator: CursorPaginator[LooseComment], seen: Iterable[LooseComment] = ()) -> IStandardStreamEventSubject[LooseComment]:
    return Stream(paginator, lambda x: x.id, seen)

def create_comment_stream(client: Client, sr: str) -> IStandardStreamEventSubject[LooseComment]:
    return make_comment_stream(get_comment_stream_paginator(client, sr))


def get_subreddit_stream_paginator(client: Client) -> CursorPaginator[Subreddit]:
    return client.p.subreddit.pulls.new().get_paginator()

def make_subreddit_stream(paginator: CursorPaginator[Subreddit], seen: Iterable[Subreddit] = ()) -> IStandardStreamEventSubject[Subreddit]:
    return Stream(paginator, lambda x: x.id, seen)

def create_subreddit_stream(client: Client) -> IStandardStreamEventSubject[Subreddit]:
    return make_subreddit_stream(get_subreddit_stream_paginator(client))
