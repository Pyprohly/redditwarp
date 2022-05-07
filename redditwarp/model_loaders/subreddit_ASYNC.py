
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from ..models.subreddit_ASYNC import Subreddit, InaccessibleSubreddit

def load_subreddit(d: Mapping[str, Any], client: Client) -> Subreddit:
    return Subreddit(d, client)

def load_potentially_inaccessible_subreddit(d: Mapping[str, Any], client: Client) -> object:
    if d['public_traffic'] is None:
        return InaccessibleSubreddit(d, client)
    return Subreddit(d, client)
