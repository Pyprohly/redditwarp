
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.subreddit_ASYNC import Subreddit
    from ..impls.stream_ASYNC import IStandardStreamEventSubject
    from ...pagination.async_paginator import CursorAsyncPaginator

from ..impls.stream_ASYNC import SimpleImprintExtractorStream


def get_user_subreddit_stream_paginator(client: Client) -> CursorAsyncPaginator[Subreddit]:
    return client.p.user.pull_subreddits.new().get_paginator()

def make_user_subreddit_stream(paginator: CursorAsyncPaginator[Subreddit], past: Optional[Iterable[Subreddit]] = None) -> IStandardStreamEventSubject[Subreddit]:
    def user_subreddit_stream_extractor(x: Subreddit) -> object:
        return x.id
    return SimpleImprintExtractorStream(paginator, user_subreddit_stream_extractor, past=past)

def create_user_subreddit_stream(client: Client) -> IStandardStreamEventSubject[Subreddit]:
    return make_user_subreddit_stream(get_user_subreddit_stream_paginator(client))
