
from __future__ import annotations
from typing import TYPE_CHECKING, Union, overload
if TYPE_CHECKING:
    from ...models.subreddit_SYNC import Subreddit
    from ..stream_SYNC import IStandardStreamEventSubject
    from ...pagination.paginator import CursorPaginator

from ...client_SYNC import Client
from ..stream_SYNC import Stream


def get_user_subreddit_stream_paginator(client: Client) -> CursorPaginator[Subreddit]:
    return client.p.user.pull_user_subreddits.new().get_paginator()

@overload
def make_user_subreddit_stream(paginator: CursorPaginator[Subreddit], /) -> IStandardStreamEventSubject[Subreddit]: ...
@overload
def make_user_subreddit_stream(client: Client, /) -> IStandardStreamEventSubject[Subreddit]: ...
def make_user_subreddit_stream(arg: Union[CursorPaginator[Subreddit], Client]) -> IStandardStreamEventSubject[Subreddit]:
    paginator: CursorPaginator[Subreddit]
    if isinstance(arg, Client):
        client = arg
        paginator = client.p.user.pull_user_subreddits.new().get_paginator()
    else:
        paginator = arg
    return Stream(paginator, lambda x: x.id)
