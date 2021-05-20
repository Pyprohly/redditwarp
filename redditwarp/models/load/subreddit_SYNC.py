
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..subreddit_SYNC import Subreddit

def load_subreddit(d: Mapping[str, Any], client: Client) -> Subreddit:
    return Subreddit(d, client)
