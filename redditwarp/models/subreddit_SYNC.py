
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .subreddit_base import BaseSubreddit, BaseInaccessibleSubreddit

class Subreddit(BaseSubreddit):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

class InaccessibleSubreddit(BaseInaccessibleSubreddit):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client
