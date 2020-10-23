
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.submission_collection_SYNC import VisualSubmissionCollection

from ...load.submission_collection_SYNC import load_visual_submission_collection

from .get_subreddit_collections_SYNC import GetSubredditCollections
from .create_SYNC import Create
from .add_post_SYNC import AddPost
from .remove_post_SYNC import RemovePost
from .reorder_SYNC import Reorder

class Collection:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.get_subreddit_collections = GetSubredditCollections(client)
        self.create = Create(client)
        self.add_post = AddPost(client)
        self.remove_post = RemovePost(client)
        self.reorder = Reorder(client)

    def fetch(self, uuid: str, include_posts: bool = True) -> VisualSubmissionCollection:
        params = {'collection_id': uuid, 'include_links': '01'[include_posts]}
        data = self._client.request('GET', '/api/v1/collections/collection', params=params)
        return load_visual_submission_collection(data, self._client)

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
