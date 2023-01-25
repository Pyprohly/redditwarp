
from __future__ import annotations
from typing import TYPE_CHECKING, Union, overload, cast
if TYPE_CHECKING:
    from ...models.submission_ASYNC import Submission
    from ...models.comment_ASYNC import LooseComment
    from ...models.subreddit_ASYNC import Subreddit
    from ..stream_ASYNC import IStandardStreamEventSubject
    from ...pagination.async_paginator import CursorAsyncPaginator

from ...client_ASYNC import Client
from ..stream_ASYNC import Stream


def get_submission_stream_paginator(client: Client, sr: str) -> CursorAsyncPaginator[Submission]:
    return client.p.subreddit.pull.new(sr).get_paginator()

@overload
def make_submission_stream(paginator: CursorAsyncPaginator[Submission], /) -> IStandardStreamEventSubject[Submission]: ...
@overload
def make_submission_stream(client: Client, sr: str, /) -> IStandardStreamEventSubject[Submission]: ...
def make_submission_stream(*args: object) -> IStandardStreamEventSubject[Submission]:
    paginator: CursorAsyncPaginator[Submission]
    if len(args) == 1:
        args = cast("tuple[CursorAsyncPaginator[Submission]]", args)
        paginator, = args
    else:
        args = cast("tuple[Client, str]", args)
        client, sr = args
        paginator = client.p.subreddit.pull.new(sr).get_paginator()
    return Stream(paginator, lambda x: x.id)


def get_comment_stream_paginator(client: Client, sr: str) -> CursorAsyncPaginator[LooseComment]:
    return client.p.subreddit.pull_new_comments(sr).get_paginator()

@overload
def make_comment_stream(paginator: CursorAsyncPaginator[LooseComment], /) -> IStandardStreamEventSubject[LooseComment]: ...
@overload
def make_comment_stream(client: Client, sr: str, /) -> IStandardStreamEventSubject[LooseComment]: ...
def make_comment_stream(*args: object) -> IStandardStreamEventSubject[LooseComment]:
    paginator: CursorAsyncPaginator[LooseComment]
    if len(args) == 1:
        args = cast("tuple[CursorAsyncPaginator[LooseComment]]", args)
        paginator, = args
    else:
        args = cast("tuple[Client, str]", args)
        client, sr = args
        paginator = client.p.subreddit.pull_new_comments(sr).get_paginator()
    return Stream(paginator, lambda x: x.id)


def get_subreddit_stream_paginator(client: Client, sr: str) -> CursorAsyncPaginator[Subreddit]:
    return client.p.subreddit.pulls.new().get_paginator()

@overload
def make_subreddit_stream(paginator: CursorAsyncPaginator[Subreddit], /) -> IStandardStreamEventSubject[Subreddit]: ...
@overload
def make_subreddit_stream(client: Client, /) -> IStandardStreamEventSubject[Subreddit]: ...
def make_subreddit_stream(arg: Union[CursorAsyncPaginator[Subreddit], Client]) -> IStandardStreamEventSubject[Subreddit]:
    paginator: CursorAsyncPaginator[Subreddit]
    if isinstance(arg, Client):
        client = arg
        paginator = client.p.subreddit.pulls.new().get_paginator()
    else:
        paginator = arg
    return Stream(paginator, lambda x: x.id)
