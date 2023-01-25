
from __future__ import annotations
from typing import TYPE_CHECKING, Union, overload, cast
if TYPE_CHECKING:
    from ...models.submission_SYNC import Submission
    from ...models.comment_SYNC import LooseComment
    from ...models.subreddit_SYNC import Subreddit
    from ..stream_SYNC import IStandardStreamEventSubject
    from ...pagination.paginator import CursorPaginator

from ...client_SYNC import Client
from ..stream_SYNC import Stream


def get_submission_stream_paginator(client: Client, sr: str) -> CursorPaginator[Submission]:
    return client.p.subreddit.pull.new(sr).get_paginator()

@overload
def make_submission_stream(paginator: CursorPaginator[Submission], /) -> IStandardStreamEventSubject[Submission]: ...
@overload
def make_submission_stream(client: Client, sr: str, /) -> IStandardStreamEventSubject[Submission]: ...
def make_submission_stream(*args: object) -> IStandardStreamEventSubject[Submission]:
    paginator: CursorPaginator[Submission]
    if len(args) == 1:
        args = cast("tuple[CursorPaginator[Submission]]", args)
        paginator, = args
    else:
        args = cast("tuple[Client, str]", args)
        client, sr = args
        paginator = client.p.subreddit.pull.new(sr).get_paginator()
    return Stream(paginator, lambda x: x.id)


def get_comment_stream_paginator(client: Client, sr: str) -> CursorPaginator[LooseComment]:
    return client.p.subreddit.pull_new_comments(sr).get_paginator()

@overload
def make_comment_stream(paginator: CursorPaginator[LooseComment], /) -> IStandardStreamEventSubject[LooseComment]: ...
@overload
def make_comment_stream(client: Client, sr: str, /) -> IStandardStreamEventSubject[LooseComment]: ...
def make_comment_stream(*args: object) -> IStandardStreamEventSubject[LooseComment]:
    paginator: CursorPaginator[LooseComment]
    if len(args) == 1:
        args = cast("tuple[CursorPaginator[LooseComment]]", args)
        paginator, = args
    else:
        args = cast("tuple[Client, str]", args)
        client, sr = args
        paginator = client.p.subreddit.pull_new_comments(sr).get_paginator()
    return Stream(paginator, lambda x: x.id)


def get_subreddit_stream_paginator(client: Client, sr: str) -> CursorPaginator[Subreddit]:
    return client.p.subreddit.pulls.new().get_paginator()

@overload
def make_subreddit_stream(paginator: CursorPaginator[Subreddit], /) -> IStandardStreamEventSubject[Subreddit]: ...
@overload
def make_subreddit_stream(client: Client, /) -> IStandardStreamEventSubject[Subreddit]: ...
def make_subreddit_stream(arg: Union[CursorPaginator[Subreddit], Client]) -> IStandardStreamEventSubject[Subreddit]:
    paginator: CursorPaginator[Subreddit]
    if isinstance(arg, Client):
        client = arg
        paginator = client.p.subreddit.pulls.new().get_paginator()
    else:
        paginator = arg
    return Stream(paginator, lambda x: x.id)
