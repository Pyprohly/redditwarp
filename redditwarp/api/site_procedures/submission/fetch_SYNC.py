
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Optional, TypeVar, Generic
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ...load.submission_SYNC import load_submission, try_load_textpost, try_load_linkpost
from ....models.submission_SYNC import Submission, LinkPost, TextPost
from ....util.base_conversion import to_base36

T = TypeVar('T')

class _Common(Generic[T]):
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> Optional[T]:
        return self.by_id(id)

    def _load_object(self, m: Mapping[str, Any]) -> Optional[T]:
        raise NotImplementedError

    def by_id(self, id: int) -> Optional[T]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Optional[T]:
        full_id36 = 't3_' + id36
        root = self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return self._load_object(children[0]['data'])
        return None

class Fetch(_Common[Submission]):
    class _AsTextPost(_Common[TextPost]):
        def _load_object(self, m: Mapping[str, Any]) -> Optional[TextPost]:
            return try_load_textpost(m, self._client)

    class _AsLinkPost(_Common[LinkPost]):
        def _load_object(self, m: Mapping[str, Any]) -> Optional[LinkPost]:
            return try_load_linkpost(m, self._client)

    def __init__(self, client: Client):
        super().__init__(client)
        self.as_textpost = self._AsTextPost(client)
        self.as_linkpost = self._AsLinkPost(client)

    def _load_object(self, m: Mapping[str, Any]) -> Optional[Submission]:
        return load_submission(m, self._client)
