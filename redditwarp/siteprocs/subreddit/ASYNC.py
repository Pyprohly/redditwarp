
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Sequence, Any, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.comment_ASYNC import LooseComment
    from ...models.subreddit_rules import SubredditRules
    from ...types import JSON_ro

from ...models.subreddit_ASYNC import Subreddit, InaccessibleSubreddit
from ...model_loaders.subreddit_ASYNC import load_subreddit, load_potentially_inaccessible_subreddit
from ...model_loaders.subreddit_rules import load_subreddit_rules
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk
from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.listing.comment_listing_async_paginator import LooseCommentListingAsyncPaginator
from ...pagination.paginators.subreddit_async1 import SubredditSearchAsyncPaginator
from ... import exceptions
from ... import http
from .pull_ASYNC import Pull
from .pulls_ASYNC import Pulls

class SubredditProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.pull: Pull = Pull(client)
        self.pulls: Pulls = Pulls(client)

    async def get(self, idn: int) -> Optional[Subreddit]:
        v = await self.get_potentially_inaccessible(idn)
        if isinstance(v, Subreddit):
            return v
        return None

    async def fetch(self, idn: int) -> Subreddit:
        v = await self.fetch_potentially_inaccessible(idn)
        if isinstance(v, Subreddit):
            return v
        if isinstance(v, InaccessibleSubreddit):
            raise exceptions.RejectedResultException
        raise Exception

    async def get_by_name(self, name: str) -> Optional[Subreddit]:
        try:
            root = await self._client.request('GET', f'/r/{name}/about')
        except exceptions.RedditError as e:
            if e.label.lower() in ('private', 'banned'):
                return None
            raise
        except http.exceptions.StatusCodeException as e:
            if e.status_code in (302, 404):
                return None
            raise
        if root['kind'] == 'Listing':
            return None
        return load_subreddit(root['data'], self._client)

    async def fetch_by_name(self, name: str) -> Subreddit:
        root = await self._client.request('GET', f'/r/{name}/about')
        if root['kind'] == 'Listing':
            raise exceptions.NoResultException('target not found')
        return load_subreddit(root['data'], self._client)

    async def get_potentially_inaccessible(self, idn: int) -> Optional[object]:
        id36 = to_base36(idn)
        full_id36 = 't5_' + id36
        root = await self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return load_potentially_inaccessible_subreddit(children[0]['data'], self._client)
        return None

    async def fetch_potentially_inaccessible(self, idn: int) -> object:
        v = await self.get_potentially_inaccessible(idn)
        if v is None:
            raise exceptions.NoResultException('target not found')
        return v

    async def get_potentially_inaccessible_by_name(self, name: str) -> Optional[object]:
        root = await self._client.request('GET', '/api/info', params={'sr_name': name})
        if children := root['data']['children']:
            return load_potentially_inaccessible_subreddit(children[0]['data'], self._client)
        return None

    async def fetch_potentially_inaccessible_by_name(self, name: str) -> object:
        v = await self.get_potentially_inaccessible_by_name(name)
        if v is None:
            raise exceptions.NoResultException('target not found')
        return v

    def bulk_fetch_potentially_inaccessible(self, ids: Iterable[int]) -> CallChunkChainingAsyncIterator[object]:
        async def mass_fetch(ids: Sequence[int]) -> Sequence[object]:
            id36s = map(to_base36, ids)
            full_id36s = map('t5_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = await self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_potentially_inaccessible_subreddit(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingAsyncIterator(AsyncCallChunk(mass_fetch, chunk) for chunk in chunked(ids, 100))

    def bulk_fetch_potentially_inaccessible_by_name(self, names: Iterable[str]) -> CallChunkChainingAsyncIterator[object]:
        async def mass_fetch(names: Sequence[str]) -> Sequence[object]:
            root = await self._client.request('GET', '/api/info', params={'sr_name': ','.join(names)})
            return [load_potentially_inaccessible_subreddit(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingAsyncIterator(AsyncCallChunk(mass_fetch, chunk) for chunk in chunked(names, 100))

    def pull_new_comments(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[LooseCommentListingAsyncPaginator, LooseComment]:
        p = LooseCommentListingAsyncPaginator(self._client, f'/r/{sr}/comments')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def get_settings(self, sr: str) -> Mapping[str, Any]:
        root = await self._client.request('GET', f'/r/{sr}/about/edit')
        if root['kind'] != 'subreddit_settings':
            raise exceptions.NoResultException('target not found')
        return root['data']

    async def update_settings(self, idn: int, settings: Mapping[str, JSON_ro]) -> None:
        id36 = to_base36(idn)
        full_id36 = 't5_' + id36
        json: Mapping[str, JSON_ro] = {**settings, 'sr': full_id36}
        await self._client.request('PATCH', '/api/v1/subreddit/update_settings', json=json)

    async def subscribe_by_id(self, idn: int) -> None:
        id36 = to_base36(idn)
        full_id36 = 't5_' + id36
        await self._client.request('POST', '/api/subscribe', data={'action': 'sub', 'sr': full_id36})

    async def subscribe_by_name(self, name: str) -> None:
        await self._client.request('POST', '/api/subscribe', data={'action': 'sub', 'sr_name': name})

    async def unsubscribe_by_id(self, idn: int) -> None:
        id36 = to_base36(idn)
        full_id36 = 't5_' + id36
        await self._client.request('POST', '/api/subscribe', data={'action': 'unsub', 'sr': full_id36})

    async def unsubscribe_by_name(self, name: str) -> None:
        await self._client.request('POST', '/api/subscribe', data={'action': 'unsub', 'sr_name': name})

    async def get_rules(self, sr: str) -> SubredditRules:
        root = await self._client.request('GET', f'/r/{sr}/about/rules')
        if 'rules' not in root:
            raise exceptions.NoResultException('target not found')
        return load_subreddit_rules(root)

    async def get_post_requirements(self, sr: str) -> Mapping[str, Any]:
        return await self._client.request('GET', f'/api/v1/{sr}/post_requirements')

    def search(self, query: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[SubredditSearchAsyncPaginator, Subreddit]:
        if not query:
            raise ValueError('query cannot be empty')
        p = SubredditSearchAsyncPaginator(self._client, '/subreddits/search', query)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def search_names(self, name: str) -> Sequence[str]:
        root = await self._client.request('GET', '/api/search_reddit_names', params={'query': name})
        return root['names']

    async def exists(self, name: str) -> bool:
        try:
            await self._client.request('GET', '/api/search_reddit_names', params={'query': name, 'exact': '1'})
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return False
            raise
        return True

    async def get_similar_subreddits(self, idn: int, n: Optional[int] = None) -> Sequence[Subreddit]:
        params = {'sr_fullnames': 't5_' + to_base36(idn)}
        if n is not None:
            params['max_recs'] = str(n)
        root = await self._client.request('GET', '/api/similar_subreddits', params=params)
        return [load_subreddit(d['data'], client=self._client) for d in root['data']['children']]
