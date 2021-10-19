
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..moderated_subreddit import ModeratedSubreddit

from ..moderated_subreddit import ModeratedUserSubreddit, ModeratedRegularSubreddit

def load_moderated_subreddit(d: Mapping[str, Any]) -> ModeratedSubreddit:
    if d['display_name'].startswith('u_'):
        return ModeratedUserSubreddit(d)
    return ModeratedRegularSubreddit(d)
