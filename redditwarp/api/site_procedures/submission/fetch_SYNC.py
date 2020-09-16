
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Optional, TypeVar, Generic
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ...load.submission import load_submission, try_load_textpost, try_load_linkpost
from ....models.submission import Submission, LinkPost, TextPost
from ....util.base_conversion import to_base36

T = TypeVar('T')

class _common(Generic[T]):
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> Optional[T]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Optional[T]:
        t_id36 = 't3_' + id36
        root = self._client.request('GET', '/api/info', params={'id': t_id36})
        children = root['data']['children']
        if not children:
            return None
        return self._load_object(children[0])

    def _load_object(self, m: Mapping[str, Any]) -> Optional[T]:
        raise NotImplementedError


class as_linkpost(_common[LinkPost]):
    def _load_object(self, m: Mapping[str, Any]) -> Optional[LinkPost]:
        return try_load_linkpost(m)

class as_textpost(_common[TextPost]):
    def _load_object(self, m: Mapping[str, Any]) -> Optional[TextPost]:
        return try_load_textpost(m)

'''
class comments_composite(_common[Submission]):
    def __init__(self, client: Client):
        self._client = client
'''#'''

class fetch(_common[Submission]):
    def __init__(self, client: Client):
        super().__init__(client)
        self.as_textpost = as_textpost(client)
        self.as_linkpost = as_linkpost(client)
        #self.comments_composite = comments_composite(client)

    def _load_object(self, m: Mapping[str, Any]) -> Optional[Submission]:
        return load_submission(m)
