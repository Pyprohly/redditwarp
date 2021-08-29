
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Any
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.custom_feed import CustomFeed as CustomFeedModel

import json

from ...models.load.custom_feed import load_custom_feed
from ... import exceptions

class CustomFeed:
    def __init__(self, client: Client):
        self._client = client
        self._json_encoder = encoder = json.JSONEncoder()
        self._json_encode = encoder.encode

    def get(self, user: str, feed: str) -> Optional[CustomFeedModel]:
        try:
            root = self._client.request('GET', f'/api/multi/user/{user}/m/{feed}')
        except exceptions.RedditAPIError as e:
            if e.codename == 'MULTI_NOT_FOUND':
                return None
            raise
        return load_custom_feed(root['data'])

    def list_own(self) -> Sequence[CustomFeedModel]:
        result = self._client.request(*'GET /api/multi/mine'.split())
        return [load_custom_feed(d['data']) for d in result]

    def list_user(self, user: str) -> Sequence[CustomFeedModel]:
        result = self._client.request(*f'GET /api/multi/user/{user}'.split())
        return [load_custom_feed(d['data']) for d in result]

    def create(self,
        user: str, feed: str,
        *,
        title: Optional[str] = None, description: Optional[str] = None,
        subreddit_names: Sequence[str] = (), private: bool = False,
    ) -> CustomFeedModel:
        json_data: dict[str, Any] = {}
        if title is not None:
            json_data['display_name'] = title
        if description is not None:
            json_data['description_md'] = description
        if subreddit_names:
            json_data['subreddits'] = {'name': nm for nm in subreddit_names}
        if not private:
            json_data['visibility'] = 'public'

        json_str = self._json_encode(json_data)
        root = self._client.request('POST', f'/api/multi/user/{user}/m/{feed}', data={'model': json_str})
        return load_custom_feed(root['data'])

    def put(self,
        user: str, feed: str,
        *,
        title: Optional[str] = None, description: Optional[str] = None,
        subreddit_names: Sequence[str] = (), private: bool = False,
    ) -> CustomFeedModel:
        json_data: dict[str, Any] = {}
        if title is not None:
            json_data['display_name'] = title
        if description is not None:
            json_data['description_md'] = description
        if subreddit_names:
            json_data['subreddits'] = [{'name': nm} for nm in subreddit_names]
        if not private:
            json_data['visibility'] = 'public'

        json_str = self._json_encode(json_data)
        root = self._client.request('PUT', f'/api/multi/user/{user}/m/{feed}', data={'model': json_str})
        return load_custom_feed(root['data'])

    def delete(self, user: str, feed: str) -> None:
        self._client.request('DELETE', f'/api/multi/user/{user}/m/{feed}')

    def duplicate(self, from_user: str, from_feed: str, to_user: str, to_feed: str, *,
            title: Optional[str] = None, description: Optional[str] = None) -> CustomFeedModel:
        data = {
            'from': f'/user/{from_user}/m/{from_feed}',
            'to': f'/user/{to_user}/m/{to_feed}',
        }
        if title is not None:
            data['display_name'] = title
        if description is not None:
            data['description_md'] = description

        root = self._client.request('POST', '/api/multi/copy', data=data)
        return load_custom_feed(root['data'])

    def check_sr_in_feed(self, user: str, feed: str, sr_name: str) -> bool:
        try:
            self._client.request('GET', f'/api/multi/user/{user}/m/{feed}/r/{sr_name}')
        except exceptions.RedditAPIError as e:
            if e.codename == 'SUBREDDIT_NOEXIST':
                return False
            raise
        return True

    def add_subreddit(self, user: str, feed: str, sr_name: str) -> None:
        json_str = self._json_encode({"name": "aa"})
        self._client.request('PUT', f'/api/multi/user/{user}/m/{feed}/r/{sr_name}',
                data={'model': json_str})

    def remove_subreddit(self, user: str, feed: str, sr_name: str) -> None:
        self._client.request('DELETE', f'/api/multi/user/{user}/m/{feed}/r/{sr_name}')
