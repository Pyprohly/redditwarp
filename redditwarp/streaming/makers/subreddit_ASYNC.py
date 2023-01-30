
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_ASYNC import Submission
    from ...models.comment_ASYNC import LooseComment
    from ...models.subreddit_ASYNC import Subreddit
    from ..stream_ASYNC import IStandardStreamEventSubject
    from ...pagination.async_paginator import CursorAsyncPaginator

from ..stream_ASYNC import Stream


def get_submission_stream_paginator(client: Client, sr: str) -> CursorAsyncPaginator[Submission]:
    return client.p.subreddit.pull.new(sr).get_paginator()

def make_submission_stream(paginator: CursorAsyncPaginator[Submission], seen: Iterable[Submission] = ()) -> IStandardStreamEventSubject[Submission]:
    return Stream(paginator, lambda x: x.id, seen)

def create_submission_stream(client: Client, sr: str) -> IStandardStreamEventSubject[Submission]:
    return make_submission_stream(get_submission_stream_paginator(client, sr))


def get_comment_stream_paginator(client: Client, sr: str) -> CursorAsyncPaginator[LooseComment]:
    return client.p.subreddit.pull_new_comments(sr).get_paginator()

def make_comment_stream(paginator: CursorAsyncPaginator[LooseComment], seen: Iterable[LooseComment] = ()) -> IStandardStreamEventSubject[LooseComment]:
    return Stream(paginator, lambda x: x.id, seen)

def create_comment_stream(client: Client, sr: str) -> IStandardStreamEventSubject[LooseComment]:
    return make_comment_stream(get_comment_stream_paginator(client, sr))


def get_subreddit_stream_paginator(client: Client) -> CursorAsyncPaginator[Subreddit]:
    return client.p.subreddit.pulls.new().get_paginator()

def make_subreddit_stream(paginator: CursorAsyncPaginator[Subreddit], seen: Iterable[Subreddit] = ()) -> IStandardStreamEventSubject[Subreddit]:
    return Stream(paginator, lambda x: x.id, seen)

def create_subreddit_stream(client: Client) -> IStandardStreamEventSubject[Subreddit]:
    return make_subreddit_stream(get_subreddit_stream_paginator(client))
