
from __future__ import annotations
from typing import Mapping, Any

from ..models.modmail import ModmailModeratedSubreddit

def load_modmail_moderated_subreddit(d: Mapping[str, Any]) -> ModmailModeratedSubreddit:
    return ModmailModeratedSubreddit(
        d=d,
        id=int(d['id'][3:], 36),
        name=d['name'],
        subscriber_count=d['subscribers'],
    )
