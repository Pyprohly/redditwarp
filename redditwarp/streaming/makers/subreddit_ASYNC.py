
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_ASYNC import Submission
    from ...models.comment_ASYNC import LooseComment
    from ...models.subreddit_ASYNC import Subreddit
    from ..impls.stream_ASYNC import IStandardStreamEventSubject
    from ...pagination.async_paginator import CursorAsyncPaginator

from ..impls.stream_ASYNC import SimpleImprintExtractorStream


def get_submission_stream_paginator(client: Client, sr: str) -> CursorAsyncPaginator[Submission]:
    return client.p.subreddit.pull.new(sr).get_paginator()

def make_submission_stream(paginator: CursorAsyncPaginator[Submission], past: Optional[Iterable[Submission]] = None) -> IStandardStreamEventSubject[Submission]:
    def submission_stream_extractor(x: Submission) -> object:
        return x.id
    return SimpleImprintExtractorStream(paginator, submission_stream_extractor, past=past)

def create_submission_stream(client: Client, sr: str) -> IStandardStreamEventSubject[Submission]:
    return make_submission_stream(get_submission_stream_paginator(client, sr))


def get_comment_stream_paginator(client: Client, sr: str) -> CursorAsyncPaginator[LooseComment]:
    return client.p.subreddit.pull_new_comments(sr).get_paginator()

def make_comment_stream(paginator: CursorAsyncPaginator[LooseComment], past: Optional[Iterable[LooseComment]] = None) -> IStandardStreamEventSubject[LooseComment]:
    def comment_stream_extractor(x: LooseComment) -> object:
        return x.id
    return SimpleImprintExtractorStream(paginator, comment_stream_extractor, past=past)

def create_comment_stream(client: Client, sr: str) -> IStandardStreamEventSubject[LooseComment]:
    return make_comment_stream(get_comment_stream_paginator(client, sr))


def get_subreddit_stream_paginator(client: Client) -> CursorAsyncPaginator[Subreddit]:
    return client.p.subreddit.pulls.new().get_paginator()

def make_subreddit_stream(paginator: CursorAsyncPaginator[Subreddit], past: Optional[Iterable[Subreddit]] = None) -> IStandardStreamEventSubject[Subreddit]:
    def subreddit_stream_extractor(x: Subreddit) -> object:
        return x.id
    return SimpleImprintExtractorStream(paginator, subreddit_stream_extractor, past=past)

def create_subreddit_stream(client: Client) -> IStandardStreamEventSubject[Subreddit]:
    return make_subreddit_stream(get_subreddit_stream_paginator(client))
