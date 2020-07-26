
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....client_sync import Client

from .pull_sync import pull

class Subreddit:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.pull = pull(client)
