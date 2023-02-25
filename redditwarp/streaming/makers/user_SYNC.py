
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit
    from ..stream_SYNC import IStandardStreamEventSubject
    from ...pagination.paginator import CursorPaginator

from ..stream_SYNC import Stream


def user_subreddit_stream_extractor(x: Subreddit) -> object:
    return x.id

def get_user_subreddit_stream_paginator(client: Client) -> CursorPaginator[Subreddit]:
    return client.p.user.pull_subreddits.new().get_paginator()

def make_user_subreddit_stream(paginator: CursorPaginator[Subreddit], past: Optional[Iterable[Subreddit]] = None, seen: Optional[Iterable[object]] = None) -> IStandardStreamEventSubject[Subreddit]:
    return Stream(paginator, user_subreddit_stream_extractor, past=past, seen=seen)

def create_user_subreddit_stream(client: Client) -> IStandardStreamEventSubject[Subreddit]:
    return make_user_subreddit_stream(get_user_subreddit_stream_paginator(client))
