
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.user_SYNC import User as _User

from .fetch_partial_SYNC import FetchPartial
from .bulk_fetch_partial_SYNC import BulkFetchPartial
from .pull_SYNC import Pull
from ...load.user_SYNC import load_user
from .... import exceptions

class User:
    def __init__(self, client: Client):
        self._client = client
        self.fetch_partial = FetchPartial(client)
        self.bulk_fetch_partial = BulkFetchPartial(client)
        self.pull = Pull(client)

    def fetch_by_name(self, name: str) -> Optional[_User]:
        try:
            root = self._client.request('GET', f'/user/{name}/about')
        except exceptions.HTTPStatusError as e:
            if e.response.status == 404:
                return None
            raise
        return load_user(root['data'], self._client)
