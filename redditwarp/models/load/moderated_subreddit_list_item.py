
from __future__ import annotations
from typing import Any, Mapping

from ..moderated_subreddit_list_item import ModeratedSubredditListItem

def load_moderated_subreddit_list_item(d: Mapping[str, Any]) -> ModeratedSubredditListItem:
    return ModeratedSubredditListItem(d)
