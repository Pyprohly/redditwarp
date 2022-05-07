
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_SYNC import Comment

from ...model_loaders.comment_SYNC import load_comment
from ...util.base_conversion import to_base36
from ...util.extract_id_from_url import extract_comment_id_from_url

class Get:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> Optional[Comment]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Optional[Comment]:
        full_id36 = 't1_' + id36
        root = self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return load_comment(children[0]['data'], self._client)
        return None

    def by_url(self, url: str) -> Optional[Comment]:
        return self(extract_comment_id_from_url(url))
