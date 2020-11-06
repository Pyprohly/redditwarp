
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....client_SYNC import Client

from .fetch_SYNC import Fetch
from .get_SYNC import Get
from .bulk_fetch_SYNC import BulkFetch

class Submission:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.fetch = Fetch(self, client)
        self.get = Get(client)
        self.bulk_fetch = BulkFetch(client)
