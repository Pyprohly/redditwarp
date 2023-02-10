
from __future__ import annotations
from typing import Any, Mapping

from ..models.moderated_subreddit import ModeratedSubreddit

def load_moderated_subreddit(d: Mapping[str, Any]) -> ModeratedSubreddit:
    return ModeratedSubreddit(d)
