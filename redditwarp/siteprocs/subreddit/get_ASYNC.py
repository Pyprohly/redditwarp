
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ...models.load.subreddit_ASYNC import load_potentially_inaccessible_subreddit
from ...util.base_conversion import to_base36

class Get:
    def __init__(self, client: Client):
        self._client = client

    async def __call__(self, id: int) -> Optional[object]:
        id36 = to_base36(id)
        return await self.by_id36(id36)

    async def by_id36(self, id36: str) -> Optional[object]:
        full_id36 = 't5_' + id36
        root = await self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return load_potentially_inaccessible_subreddit(children[0]['data'], self._client)
        return None
