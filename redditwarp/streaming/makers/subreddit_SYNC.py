
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission
    from ...models.comment_SYNC import LooseComment
    from ...models.subreddit_SYNC import Subreddit
    from ..stream_SYNC import IStandardStreamEventSubject

from ..stream_SYNC import Stream


def make_submission_stream(client: Client, sr: str) -> IStandardStreamEventSubject[Submission]:
    it = client.p.subreddit.pull.new(sr)
    paginator = it.get_paginator()
    return Stream(paginator, lambda x: x.id)

def make_comment_stream(client: Client, sr: str) -> IStandardStreamEventSubject[LooseComment]:
    it = client.p.subreddit.pull_new_comments(sr)
    paginator = it.get_paginator()
    return Stream(paginator, lambda x: x.id)

def make_subreddit_stream(client: Client) -> IStandardStreamEventSubject[Subreddit]:
    it = client.p.subreddit.pulls.new()
    paginator = it.get_paginator()
    return Stream(paginator, lambda x: x.id)
