
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ....models.comment_SYNC import Comment
from ....util.base_conversion import to_base36
from ....util.extract_id36_from_url import extract_comment_id36_from_url

class Fetch:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> Optional[Comment]:
        return self.by_id(id)

    def _load_object(self, m: Mapping[str, Any]) -> Optional[Comment]:
        return Comment(m, self._client)

    def by_id(self, id: int) -> Optional[Comment]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Optional[Comment]:
        full_id36 = 't1_' + id36
        root = self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return self._load_object(children[0]['data'])
        return None

    def by_url(self, url: str) -> Optional[Comment]:
        return self.by_id36(extract_comment_id36_from_url(url))
