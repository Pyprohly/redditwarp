
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ....models.subreddit_SYNC import Subreddit
from ....util.base_conversion import to_base36
from .... import exceptions

class Fetch:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> Optional[Subreddit]:
        return self.by_id(id)

    def _load_object(self, m: Mapping[str, Any]) -> Optional[Subreddit]:
        return Subreddit(m, self._client)

    def by_id(self, id: int) -> Optional[Subreddit]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Optional[Subreddit]:
        full_id36 = 't5_' + id36
        root = self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return self._load_object(children[0]['data'])
        return None

    def by_name(self, name: str) -> Optional[Subreddit]:
        try:
            root = self._client.request('GET', f'/r/{name}/about')
        except (
            # A special subreddit name (`all`, `popular`, `friends`, `mod`) was specified.
            exceptions.HTTPStatusError,
            # Name contained invalid characters.
            exceptions.UnacceptableHTMLDocumentReceivedError,
        ) as e:
            if e.response.status != 404:
                raise
            return None
        if root['kind'] == 'Listing':
            # Subreddit was not found.
            return None
        return Subreddit(root['data'], self._client)
