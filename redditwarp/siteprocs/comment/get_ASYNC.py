
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.comment_ASYNC import Comment

from ...model_loaders.comment_ASYNC import load_comment
from ...util.base_conversion import to_base36
from ...util.extract_id_from_url import extract_comment_id_from_url

class Get:
    def __init__(self, client: Client) -> None:
        self._client = client

    async def __call__(self, idy: Union[int, str]) -> Optional[Comment]:
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        return await self.by_id36(id36)

    async def by_id36(self, id36: str) -> Optional[Comment]:
        full_id36 = 't1_' + id36
        root = await self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return load_comment(children[0]['data'], self._client)
        return None

    async def by_url(self, url: str) -> Optional[Comment]:
        return await self(extract_comment_id_from_url(url))
