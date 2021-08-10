
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ...models.load.comment_SYNC import load_normal_comment
from ...models.comment_SYNC import NormalComment
from ...util.base_conversion import to_base36
from ...util.extract_id_from_url import extract_comment_id_from_url

class Get:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> Optional[NormalComment]:
        return self.by_id(id)

    def by_id(self, id: int) -> Optional[NormalComment]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Optional[NormalComment]:
        full_id36 = 't1_' + id36
        root = self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return load_normal_comment(children[0]['data'], self._client)
        return None

    def by_url(self, url: str) -> Optional[NormalComment]:
        return self.by_id(extract_comment_id_from_url(url))
