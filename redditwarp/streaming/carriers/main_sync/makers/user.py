
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....client_SYNC import Client
    from .....models.subreddit_SYNC import Subreddit
    from ..stream import IStandardStreamEventSubject

from ..stream import Stream


def make_user_subreddit_stream(client: Client) -> IStandardStreamEventSubject[Subreddit]:
    it = client.p.user.pull_user_subreddits.new()
    paginator = it.get_paginator()
    return Stream(paginator, lambda x: x.id)
