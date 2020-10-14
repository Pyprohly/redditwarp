
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....client_SYNC import Client

from .pull_SYNC import Pull

class FrontPage:
    def __init__(self, client: Client):
        self._client = client
        self.pull = Pull(client)
