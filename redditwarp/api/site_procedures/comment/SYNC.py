
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....client_SYNC import Client

from .fetch_SYNC import Fetch
from .bulk_fetch_SYNC import BulkFetch

class Comment:
    def __init__(self, client: Client):
        self._client = client
        self.fetch = Fetch(client)
        self.bulk_fetch = BulkFetch(client)