
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit

from ...models.load.subreddit_SYNC import load_subreddit
from ...util.base_conversion import to_base36

class Get:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> Optional[Subreddit]:
        return self.by_id(id)

    def by_id(self, id: int) -> Optional[Subreddit]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Optional[Subreddit]:
        full_id36 = 't5_' + id36
        root = self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return load_subreddit(children[0]['data'], self._client)
        return None
