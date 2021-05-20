
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ..subreddit_ASYNC import Subreddit

def load_subreddit(d: Mapping[str, Any], client: Client) -> Subreddit:
    return Subreddit(d, client)
