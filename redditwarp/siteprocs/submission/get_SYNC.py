
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Optional, TypeVar, Generic, Union
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ...model_loaders.submission_SYNC import load_submission
from ...models.submission_SYNC import Submission, LinkPost, TextPost
from ...util.base_conversion import to_base36
from ...util.extract_id_from_url import extract_submission_id_from_url

T = TypeVar('T')

class Common(Generic[T]):
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, idy: Union[int, str]) -> Optional[T]:
        id36 = x if isinstance((x := idy), str) else to_base36(x)
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



class Get(Common[Submission]):
    class AsTextPost(Common[TextPost]):
        def _load_object(self, m: Mapping[str, Any]) -> Optional[TextPost]:
            post = load_submission(m, self._client)
            if isinstance(post, TextPost):
                return post
            return None

    class AsLinkPost(Common[LinkPost]):
        def _load_object(self, m: Mapping[str, Any]) -> Optional[LinkPost]:
            post = load_submission(m, self._client)
            if isinstance(post, LinkPost):
                return post
            return None

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.as_textpost: Get.AsTextPost = self.AsTextPost(client)
        self.as_linkpost: Get.AsLinkPost = self.AsLinkPost(client)

    def _load_object(self, m: Mapping[str, Any]) -> Optional[Submission]:
        return load_submission(m, self._client)
