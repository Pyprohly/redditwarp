
from __future__ import annotations
from typing import Mapping, Any

from ..models.modmail import ModeratedSubreddit

def load_moderated_subreddit(d: Mapping[str, Any]) -> ModeratedSubreddit:
    return ModeratedSubreddit(
        d=d,
        id=int(d['id'][3:], 36),
        name=d['name'],
        subscriber_count=d['subscribers'],
    )
