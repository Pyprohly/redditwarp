
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....client_sync import Client

from .fetch_sync import fetch

class Submission:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.fetch = fetch(client)
