
from __future__ import annotations
from typing import Sequence

from .submission_draft import SubmissionDraft, SubmissionDraftList as BaseSubmissionDraftList
from .subreddit_SYNC import Subreddit

class SubmissionDraftList(BaseSubmissionDraftList):
    @property
    def subreddits(self) -> Sequence[Subreddit]:
        return self.__subreddits

    def __init__(self,
        drafts: Sequence[SubmissionDraft],
        subreddits: Sequence[Subreddit],
    ) -> None:
        super().__init__(drafts, subreddits)
        self.__subreddits: Sequence[Subreddit] = subreddits
