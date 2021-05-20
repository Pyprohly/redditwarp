
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, TypeVar, Generic
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from .SYNC import Submission as Outer

from ...models.load.submission_SYNC import load_submission, try_load_textpost, try_load_linkpost
from ...models.submission_SYNC import Submission, LinkPost, TextPost
from ...util.base_conversion import to_base36
from ...util.extract_id36_from_url import extract_submission_id36_from_url
from ...exceptions import NoResultException, ClientRejectedResultException

T = TypeVar('T')

class _Common(Generic[T]):
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> T:
        return self.by_id(id)

    def _load_object(self, m: Mapping[str, Any]) -> T:
        raise NotImplementedError

    def by_id(self, id: int) -> T:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> T:
        full_id36 = 't3_' + id36
        root = self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return self._load_object(children[0]['data'])
        raise NoResultException('target not found')

    def by_url(self, url: str) -> T:
        return self.by_id36(extract_submission_id36_from_url(url))

class Fetch(_Common[Submission]):
    class _AsTextPost(_Common[TextPost]):
        def _load_object(self, m: Mapping[str, Any]) -> TextPost:
            v = try_load_textpost(m, self._client)
            if v is None:
                raise ClientRejectedResultException('the submission is not a text post')
            return v

    class _AsLinkPost(_Common[LinkPost]):
        def _load_object(self, m: Mapping[str, Any]) -> LinkPost:
            v = try_load_linkpost(m, self._client)
            if v is None:
                raise ClientRejectedResultException('the submission is not a link post')
            return v

    def __init__(self, outer: Outer, client: Client):
        super().__init__(client)
        self.as_textpost = self._AsTextPost(client)
        self.as_linkpost = self._AsLinkPost(client)

    def _load_object(self, m: Mapping[str, Any]) -> Submission:
        return load_submission(m, self._client)
