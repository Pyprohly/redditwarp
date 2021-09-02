
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..submission_draft_SYNC import DraftList
from .submission_draft import load_draft
from .subreddit_SYNC import load_subreddit

def load_draft_list(d: Mapping[str, Any], client: Client) -> DraftList:
    drafts = [load_draft(m) for m in d['drafts']]
    subreddits = [load_subreddit(m, client) for m in d['subreddits']]
    return DraftList(drafts, subreddits)
