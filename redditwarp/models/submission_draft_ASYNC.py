
from __future__ import annotations
from typing import Sequence

from .submission_draft import Draft, DraftList as BaseDraftList
from .subreddit_ASYNC import Subreddit

class DraftList(BaseDraftList):
    @property
    def subreddits(self) -> Sequence[Subreddit]:
        return self.__subreddits

    def __init__(self,
        drafts: Sequence[Draft],
        subreddits: Sequence[Subreddit],
    ) -> None:
        super().__init__(drafts, subreddits)
        self.__subreddits: Sequence[Subreddit] = subreddits
