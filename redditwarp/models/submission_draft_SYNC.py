
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
    from .submission_draft import Draft

from .submission_draft_base import GenericBaseDraftList
from .subreddit_SYNC import Subreddit

class DraftList(GenericBaseDraftList[Subreddit]):
    def __init__(self,
        drafts: Sequence[Draft],
        subreddits: Sequence[Subreddit],
    ):
        super().__init__(drafts, subreddits)
