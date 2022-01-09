
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ..submission_draft_ASYNC import DraftList
from .submission_draft import load_draft
from .subreddit_ASYNC import load_subreddit

def load_draft_list(d: Mapping[str, Any], client: Client) -> DraftList:
    drafts = [load_draft(m) for m in d['drafts']]
    subreddits = [load_subreddit(m, client) for m in d['subreddits']]
    return DraftList(drafts, subreddits)
