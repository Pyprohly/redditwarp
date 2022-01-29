
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Sequence, Any, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.subreddit_ASYNC import Subreddit
    from ...models.comment_ASYNC import ExtraSubmissionFieldsComment
    from ...models.subreddit_rules import SubredditRules
    from ...models.moderator_list import ModeratorListItem

from ...models.load.subreddit_ASYNC import load_subreddit, load_potentially_inaccessible_subreddit
from ...models.load.subreddit_rules import load_subreddit_rules
from ...models.load.moderator_list import load_moderator_list_item
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.call_chunk_ASYNC import CallChunk
from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.listing.comment_listing_async_paginator import ExtraSubmissionFieldsCommentListingAsyncPaginator
from ...pagination.implementations.subreddit_async import ExploreSubredditsAsyncPaginator
from ... import exceptions
from ... import http
from ...http.util.json_load import json_loads_response
from .fetch_ASYNC import Fetch
from .get_ASYNC import Get
from .pull_ASYNC import Pull
from .pulls_ASYNC import Pulls

class SubredditProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.get: Get = Get(client)
        self.fetch: Fetch = Fetch(client)
        self.pull: Pull = Pull(client)
        self.pulls: Pulls = Pulls(client)

    async def get_by_name(self, name: str) -> Optional[Subreddit]:
        if not name:
            raise ValueError('`name` must not be empty')
        try:
            root = await self._client.request('GET', f'/r/{name}/about')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise

        if root['kind'] != 't5':
            return None

        return load_subreddit(root['data'], self._client)

    async def fetch_by_name(self, name: str) -> Subreddit:
        root = await self._client.request('GET', f'/r/{name}/about')
        if root['kind'] == 'Listing':
            raise exceptions.NoResultException('target not found')
        return load_subreddit(root['data'], self._client)

    def bulk_fetch(self, ids: Iterable[int]) -> CallChunkChainingAsyncIterator[object]:
        async def mass_fetch(ids: Sequence[int]) -> Sequence[object]:
            id36s = map(to_base36, ids)
            full_id36s = map('t5_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = await self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_potentially_inaccessible_subreddit(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingAsyncIterator(CallChunk(mass_fetch, chunk) for chunk in chunked(ids, 100))

    def bulk_fetch_by_name(self, names: Iterable[str]) -> CallChunkChainingAsyncIterator[object]:
        async def mass_fetch(names: Sequence[str]) -> Sequence[object]:
            root = await self._client.request('GET', '/api/info', params={'sr_name': ','.join(names)})
            return [load_potentially_inaccessible_subreddit(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingAsyncIterator(CallChunk(mass_fetch, chunk) for chunk in chunked(names, 100))

    def pull_new_comments(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[ExtraSubmissionFieldsCommentListingAsyncPaginator, ExtraSubmissionFieldsComment]:
        p = ExtraSubmissionFieldsCommentListingAsyncPaginator(self._client, f'/r/{sr}/comments')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def get_settings(self, sr: str) -> Mapping[str, Any]:
        root = await self._client.request('GET', f'/r/{sr}/about/edit')
        if root['kind'] != 'subreddit_settings':
            raise exceptions.NoResultException('target not found')
        return root['data']

    async def update_settings(self, data: Mapping[str, Any]) -> None:
        await self._client.request('PATCH', '/api/v1/subreddit/update_settings', json=data)

    async def DEFUNCT__trending_subreddit_names(self) -> Sequence[str]:
        req = self._client.http.session.make_request('GET', 'https://reddit.com/api/trending_subreddits.json')
        resp = await self._client.http.send(req)
        jdata = json_loads_response(resp)
        return jdata['subreddit_names']

    async def subscribe_by_name(self, sr: str) -> None:
        await self._client.request('POST', '/api/subscribe', data={'action': 'sub', 'sr_name': sr})

    async def subscribe_by_id(self, idn: int) -> None:
        id36 = to_base36(idn)
        full_id36 = 't5_' + id36
        await self._client.request('POST', '/api/subscribe', data={'action': 'sub', 'sr': full_id36})

    async def unsubscribe_by_name(self, sr: str) -> None:
        await self._client.request('POST', '/api/subscribe', data={'action': 'unsub', 'sr_name': sr})

    async def unsubscribe_by_id(self, idn: int) -> None:
        id36 = to_base36(idn)
        full_id36 = 't5_' + id36
        await self._client.request('POST', '/api/subscribe', data={'action': 'unsub', 'sr': full_id36})

    async def get_rules(self, sr: str) -> SubredditRules:
        root = await self._client.request('GET', f'/r/{sr}/about/rules')
        if 'rules' not in root:
            raise exceptions.NoResultException('target not found')
        return load_subreddit_rules(root)

    async def get_post_requirements(self, sr: str) -> Mapping[str, Any]:
        return await self._client.request('GET', f'/api/v1/{sr}/post_requirements')

    def explore(self, query: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[ExploreSubredditsAsyncPaginator, Subreddit]:
        if not query:
            raise ValueError('query cannot be empty')
        p = ExploreSubredditsAsyncPaginator(self._client, '/subreddits/search', query)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def explore_names(self, name: str) -> Sequence[str]:
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

    async def list_moderators(self, sr: str) -> Sequence[ModeratorListItem]:
        root = await self._client.request('GET', f'/r/{sr}/about/moderators')
        return [load_moderator_list_item(d) for d in root['data']['children']]
