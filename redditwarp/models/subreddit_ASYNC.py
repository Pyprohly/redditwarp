
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from .subreddit import (
    Subreddit as BaseSubreddit,
    InaccessibleSubreddit as BaseInaccessibleSubreddit,
)

class Subreddit(BaseSubreddit):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client
        ("")

Community = Subreddit

class InaccessibleSubreddit(BaseInaccessibleSubreddit):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client
        ("")

InaccessibleCommunity = InaccessibleSubreddit
