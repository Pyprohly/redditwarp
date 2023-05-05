
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, TypeVar, Generic, Union
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from .ASYNC import SubmissionProcedures

from ...model_loaders.submission_ASYNC import load_submission
from ...models.submission_ASYNC import Submission, LinkPost, TextPost
from ...util.base_conversion import to_base36
from ...util.extract_id_from_url import extract_submission_id_from_url
from ...exceptions import NoResultException, RejectedResultException

T = TypeVar('T')

class Common(Generic[T]):
    def __init__(self, client: Client) -> None:
        self._client = client

    async def __call__(self, idy: Union[int, str]) -> T:
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        return await self.by_id36(id36)

    def _load_object(self, m: Mapping[str, Any]) -> T:
        raise NotImplementedError

    async def by_id36(self, id36: str) -> T:
        full_id36 = 't3_' + id36
        root = await self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return self._load_object(children[0]['data'])
        raise NoResultException('target not found')

    async def by_url(self, url: str) -> T:
        return await self(extract_submission_id_from_url(url))



class Fetch(Common[Submission]):
    class AsTextPost(Common[TextPost]):
        def _load_object(self, m: Mapping[str, Any]) -> TextPost:
            post = load_submission(m, self._client)
            if isinstance(post, TextPost):
                return post
            raise RejectedResultException('the submission is not a text post')

    class AsLinkPost(Common[LinkPost]):
        def _load_object(self, m: Mapping[str, Any]) -> LinkPost:
            post = load_submission(m, self._client)
            if isinstance(post, LinkPost):
                return post
            raise RejectedResultException('the submission is not a link post')

    def __init__(self, outer: SubmissionProcedures, client: Client) -> None:
        super().__init__(client)
        self.as_textpost: Fetch.AsTextPost = self.AsTextPost(client)
        self.as_linkpost: Fetch.AsLinkPost = self.AsLinkPost(client)

    def _load_object(self, m: Mapping[str, Any]) -> Submission:
        return load_submission(m, self._client)
