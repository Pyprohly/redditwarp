
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_collection_ASYNC import SubmissionCollectionInfo, SubmissionCollection

from functools import cached_property

from ...model_loaders.submission_collection_ASYNC import load_submission_collection_info, load_submission_collection
from ...util.base_conversion import to_base36
from .create_ASYNC import Create
from .add_post_ASYNC import AddPost
from .remove_post_ASYNC import RemovePost
from .reorder_ASYNC import Reorder

class CollectionProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.create: Create = Create(client)
        self.add_post: AddPost = AddPost(client)
        self.remove_post: RemovePost = RemovePost(client)
        self.reorder: Reorder = Reorder(client)

    async def get_full(self, uuid: str) -> Optional[SubmissionCollection]:
        params = {'collection_id': uuid}
        root = await self._client.request('GET', '/api/v1/collections/collection', params=params)
        if len(root) < 3:
            return None
        return load_submission_collection(root, self._client)

    async def get_info(self, uuid: str) -> Optional[SubmissionCollectionInfo]:
        params = {'collection_id': uuid, 'include_links': '0'}
        root = await self._client.request('GET', '/api/v1/collections/collection', params=params)
        if len(root) < 3:
            return None
        return load_submission_collection_info(root, self._client)

    class GetSubredditCollectionsInfo:
        def __init__(self, outer: CollectionProcedures) -> None:
            self._client = outer._client

        async def __call__(self, id: int) -> Sequence[SubmissionCollectionInfo]:
            id36 = to_base36(id)
            return await self.by_id36(id36)

        async def by_id36(self, id36: str) -> Sequence[SubmissionCollectionInfo]:
            params = {'sr_fullname': 't5_' + id36}
            root = await self._client.request('GET', '/api/v1/collections/subreddit_collections', params=params)
            return [load_submission_collection_info(d, self._client) for d in root]

    get_subreddit_collections_info: cached_property[GetSubredditCollectionsInfo] = \
            cached_property(GetSubredditCollectionsInfo)

    async def delete(self, uuid: str) -> None:
        params = {'collection_id': uuid}
        await self._client.request('POST', '/api/v1/collections/delete_collection', params=params)

    async def set_title(self, uuid: str, title: str) -> None:
        params = {'collection_id': uuid, 'title': title}
        await self._client.request('POST', '/api/v1/collections/update_collection_title', params=params)

    async def set_description(self, uuid: str, desc: str) -> None:
        params = {'collection_id': uuid, 'description': desc}
        await self._client.request('POST', '/api/v1/collections/update_collection_description', params=params)

    async def set_display_layout(self, uuid: str, layout: Optional[str]) -> None:
        params = {'collection_id': uuid}
        if layout is not None:
            params['display_layout'] = layout
        await self._client.request('POST', '/api/v1/collections/update_collection_display_layout', params=params)

    async def follow(self, uuid: str) -> None:
        params = {'follow': '1', 'collection_id': uuid}
        await self._client.request('POST', '/api/v1/collections/follow_collection', params=params)

    async def unfollow(self, uuid: str) -> None:
        params = {'follow': '0', 'collection_id': uuid}
        await self._client.request('POST', '/api/v1/collections/follow_collection', params=params)
