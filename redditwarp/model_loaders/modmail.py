
from __future__ import annotations
from typing import Mapping, Any

from ..models.modmail import ModmailSubreddit

def load_modmail_subreddit(d: Mapping[str, Any]) -> ModmailSubreddit:
    return ModmailSubreddit(
        d=d,
        id=int(d['id'][3:], 36),
        name=d['name'],
        subscriber_count=d['subscribers'],
    )
