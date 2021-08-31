
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_collection_SYNC import SubmissionCollectionDetails, SubmissionCollection

from functools import cached_property

from ...models.load.submission_collection_SYNC import load_submission_collection_details, load_submission_collection
from ...util.base_conversion import to_base36
from .create_SYNC import Create
from .add_post_SYNC import AddPost
from .remove_post_SYNC import RemovePost
from .reorder_SYNC import Reorder

class Collection:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.create = Create(client)
        self.add_post = AddPost(client)
        self.remove_post = RemovePost(client)
        self.reorder = Reorder(client)

    def get(self, uuid: str) -> Optional[SubmissionCollection]:
        params = {'collection_id': uuid}
        root = self._client.request('GET', '/api/v1/collections/collection', params=params)
        if len(root) < 3:
            return None
        return load_submission_collection(root, self._client)

    def get_unfilled(self, uuid: str) -> Optional[SubmissionCollectionDetails]:
        params = {'collection_id': uuid, 'include_links': '0'}
        root = self._client.request('GET', '/api/v1/collections/collection', params=params)
        if len(root) < 3:
            return None
        return load_submission_collection_details(root, self._client)

    class _get_subreddit_collections_details:
        def __init__(self, outer: Collection):
            self._client = outer._client

        def __call__(self, id: int) -> Sequence[SubmissionCollectionDetails]:
            id36 = to_base36(id)
            return self.by_id36(id36)

        def by_id36(self, id36: str) -> Sequence[SubmissionCollectionDetails]:
            params = {'sr_fullname': 't5_' + id36}
            root = self._client.request('GET', '/api/v1/collections/subreddit_collections', params=params)
            return [load_submission_collection_details(d, self._client) for d in root]

    get_subreddit_collections_details = cached_property(_get_subreddit_collections_details)

    def delete(self, uuid: str) -> None:
        params = {'collection_id': uuid}
        self._client.request('POST', '/api/v1/collections/delete_collection', params=params)

    def set_title(self, uuid: str, title: str) -> None:
        params = {'collection_id': uuid, 'title': title}
        self._client.request('POST', '/api/v1/collections/update_collection_title', params=params)

    def set_description(self, uuid: str, desc: str) -> None:
        params = {'collection_id': uuid, 'description': desc}
        self._client.request('POST', '/api/v1/collections/update_collection_description', params=params)

    def set_display_layout(self, uuid: str, layout: Optional[str]) -> None:
        params = {'collection_id': uuid}
        if layout is not None:
            params['display_layout'] = layout
        self._client.request('POST', '/api/v1/collections/update_collection_display_layout', params=params)

    def follow(self, uuid: str) -> None:
        params = {'follow': '1'}
        self._client.request('POST', '/api/v1/collections/follow_collection', params=params)

    def unfollow(self, uuid: str) -> None:
        params = {'follow': '0'}
        self._client.request('POST', '/api/v1/collections/follow_collection', params=params)
