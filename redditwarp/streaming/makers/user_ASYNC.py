
from __future__ import annotations
from typing import TYPE_CHECKING, Union, overload
if TYPE_CHECKING:
    from ...models.subreddit_ASYNC import Subreddit
    from ..stream_ASYNC import IStandardStreamEventSubject
    from ...pagination.async_paginator import CursorAsyncPaginator

from ...client_ASYNC import Client
from ..stream_ASYNC import Stream


def get_user_subreddit_stream_paginator(client: Client) -> CursorAsyncPaginator[Subreddit]:
    return client.p.user.pull_user_subreddits.new().get_paginator()

@overload
def make_user_subreddit_stream(paginator: CursorAsyncPaginator[Subreddit], /) -> IStandardStreamEventSubject[Subreddit]: ...
@overload
def make_user_subreddit_stream(client: Client, /) -> IStandardStreamEventSubject[Subreddit]: ...
def make_user_subreddit_stream(arg: Union[CursorAsyncPaginator[Subreddit], Client]) -> IStandardStreamEventSubject[Subreddit]:
    paginator: CursorAsyncPaginator[Subreddit]
    if isinstance(arg, Client):
        client = arg
        paginator = client.p.user.pull_user_subreddits.new().get_paginator()
    else:
        paginator = arg
    return Stream(paginator, lambda x: x.id)
