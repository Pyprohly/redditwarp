
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Any, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.custom_feed_ASYNC import CustomFeed

import json

from ...model_loaders.custom_feed_ASYNC import load_custom_feed
from ... import exceptions
from ... import http
from ...iterators.chunking import chunked
from ...iterators.call_chunk_calling_async_iterator import CallChunkCallingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk

class CustomFeedProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._json_encoder = encoder = json.JSONEncoder()
        self._json_encode = encoder.encode

    async def fetch(self, user: str, feed: str) -> Optional[CustomFeed]:
        root = await self._client.request('GET', f'/api/multi/user/{user}/m/{feed}')
        return load_custom_feed(root['data'], self._client)

    async def get(self, user: str, feed: str) -> Optional[CustomFeed]:
        try:
            root = await self._client.request('GET', f'/api/multi/user/{user}/m/{feed}')
        except exceptions.RedditError as e:
            if e.label == 'MULTI_NOT_FOUND':
                return None
            raise
        return load_custom_feed(root['data'], self._client)

    async def retrieve_mine(self) -> Sequence[CustomFeed]:
        result = await self._client.request('GET', '/api/multi/mine')
        return [load_custom_feed(d['data'], self._client) for d in result]

    async def retrieve(self, user: str) -> Sequence[CustomFeed]:
        result = await self._client.request('GET', f'/api/multi/user/{user}')
        return [load_custom_feed(d['data'], self._client) for d in result]

    async def create(self,
        user: str,
        feed: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        subreddit_names: Sequence[str] = (),
        exposed: bool = False,
    ) -> CustomFeed:
        json_data: dict[str, Any] = {}
        if title is not None:
            json_data['display_name'] = title
        if description is not None:
            json_data['description_md'] = description
        if subreddit_names:
            json_data['subreddits'] = {'name': nm for nm in subreddit_names}
        if not exposed:
            json_data['visibility'] = 'public'

        json_str = self._json_encode(json_data)
        root = await self._client.request('POST', f'/api/multi/user/{user}/m/{feed}', data={'model': json_str})
        return load_custom_feed(root['data'], self._client)

    async def put(self,
        user: str,
        feed: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        subreddit_names: Sequence[str] = (),
        exposed: bool = False,
    ) -> CustomFeed:
        json_data: dict[str, Any] = {}
        if title is not None:
            json_data['display_name'] = title
        if description is not None:
            json_data['description_md'] = description
        if subreddit_names:
            json_data['subreddits'] = [{'name': nm} for nm in subreddit_names]
        if not exposed:
            json_data['visibility'] = 'public'

        json_str = self._json_encode(json_data)
        root = await self._client.request('PUT', f'/api/multi/user/{user}/m/{feed}', data={'model': json_str})
        return load_custom_feed(root['data'], self._client)

    async def delete(self, user: str, feed: str) -> None:
        await self._client.request('DELETE', f'/api/multi/user/{user}/m/{feed}')

    async def copy(self, src_user: str, src_feed: str, dst_user: str, dst_feed: str, *,
            title: Optional[str] = None, description: Optional[str] = None) -> CustomFeed:
        data = {
            'from': f'/user/{src_user}/m/{src_feed}',
            'to': f'/user/{dst_user}/m/{dst_feed}',
        }
        if title is not None:
            data['display_name'] = title
        if description is not None:
            data['description_md'] = description

        root = await self._client.request('POST', '/api/multi/copy', data=data)
        return load_custom_feed(root['data'], self._client)

    async def contains(self, user: str, feed: str, sr_name: str) -> bool:
        try:
            await self._client.request('GET', f'/api/multi/user/{user}/m/{feed}/r/{sr_name}')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 500:
                return False
            raise
        except exceptions.RedditError as e:
            if e.label == 'SUBREDDIT_NOEXIST':
                return False
            raise
        return True

    async def add_item(self, user: str, feed: str, sr_name: str) -> None:
        json_str = self._json_encode({"name": "abc"})
        await self._client.request('PUT', f'/api/multi/user/{user}/m/{feed}/r/{sr_name}', data={'model': json_str})

    def bulk_add_item(self, user: str, feed: str, sr_names: Iterable[str]) -> CallChunkCallingAsyncIterator[None]:
        async def mass_add_item(sr_names: Sequence[str]) -> None:
            data = {'path': f'/user/{user}/m/{feed}', 'sr_names': (','.join(sr_names))}
            await self._client.request('POST', '/api/multi/add_srs_bulk', data=data)

        return CallChunkCallingAsyncIterator(AsyncCallChunk(mass_add_item, chunk) for chunk in chunked(sr_names, 300))

    async def remove_item(self, user: str, feed: str, sr_name: str) -> None:
        await self._client.request('DELETE', f'/api/multi/user/{user}/m/{feed}/r/{sr_name}')
