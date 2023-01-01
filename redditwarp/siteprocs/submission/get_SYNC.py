
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Optional, TypeVar, Generic
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ...model_loaders.submission_SYNC import load_submission
from ...models.submission_SYNC import Submission, LinkPost, TextPost
from ...util.base_conversion import to_base36
from ...util.extract_id_from_url import extract_submission_id_from_url

T = TypeVar('T')

class _Common(Generic[T]):
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, id: int) -> Optional[T]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def _load_object(self, m: Mapping[str, Any]) -> Optional[T]:
        raise NotImplementedError

    def by_id36(self, id36: str) -> Optional[T]:
        full_id36 = 't3_' + id36
        root = self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return self._load_object(children[0]['data'])
        return None

    def by_url(self, url: str) -> Optional[T]:
        return self(extract_submission_id_from_url(url))

class Get(_Common[Submission]):
    class _AsTextPost(_Common[TextPost]):
        def _load_object(self, m: Mapping[str, Any]) -> Optional[TextPost]:
            post = load_submission(m, self._client)
            if isinstance(post, TextPost):
                return post
            return None

    class _AsLinkPost(_Common[LinkPost]):
        def _load_object(self, m: Mapping[str, Any]) -> Optional[LinkPost]:
            post = load_submission(m, self._client)
            if isinstance(post, LinkPost):
                return post
            return None

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.as_textpost: Get._AsTextPost = self._AsTextPost(client)
        self.as_linkpost: Get._AsLinkPost = self._AsLinkPost(client)

    def _load_object(self, m: Mapping[str, Any]) -> Optional[Submission]:
        return load_submission(m, self._client)
