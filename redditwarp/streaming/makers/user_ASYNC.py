
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.subreddit_ASYNC import Subreddit
    from ..stream_ASYNC import IStandardStreamEventSubject
    from ...pagination.async_paginator import CursorAsyncPaginator

from ..stream_ASYNC import Stream


def get_user_subreddit_stream_paginator(client: Client) -> CursorAsyncPaginator[Subreddit]:
    return client.p.user.pull_user_subreddits.new().get_paginator()

def make_user_subreddit_stream(paginator: CursorAsyncPaginator[Subreddit], seen: Iterable[Subreddit] = ()) -> IStandardStreamEventSubject[Subreddit]:
    return Stream(paginator, lambda x: x.id, seen)

def create_user_subreddit_stream(client: Client) -> IStandardStreamEventSubject[Subreddit]:
    return make_user_subreddit_stream(get_user_subreddit_stream_paginator(client))
