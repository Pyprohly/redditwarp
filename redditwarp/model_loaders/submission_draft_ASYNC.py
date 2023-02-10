
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from ..models.submission_draft_ASYNC import SubmissionDraftList
from .submission_draft import load_submission_draft
from .subreddit_ASYNC import load_subreddit

def load_submission_draft_list(d: Mapping[str, Any], client: Client) -> SubmissionDraftList:
    drafts = [load_submission_draft(m) for m in d['drafts']]
    subreddits = [load_subreddit(m, client) for m in d['subreddits']]
    return SubmissionDraftList(drafts, subreddits)
