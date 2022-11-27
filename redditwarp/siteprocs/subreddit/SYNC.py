
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Sequence, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit
    from ...models.comment_SYNC import LooseComment
    from ...models.subreddit_rules import SubredditRules

from ...model_loaders.subreddit_SYNC import load_subreddit, load_potentially_inaccessible_subreddit
from ...model_loaders.subreddit_rules import load_subreddit_rules
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk import CallChunk
from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.listing.comment_listing_paginator import LooseCommentListingPaginator
from ...pagination.paginators.subreddit_sync1 import SubredditSearchPaginator
from ... import exceptions
from ... import http
from .fetch_SYNC import Fetch
from .get_SYNC import Get
from .pull_SYNC import Pull
from .pulls_SYNC import Pulls

class SubredditProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.get: Get = Get(client)
        self.fetch: Fetch = Fetch(self, client)
        self.pull: Pull = Pull(client)
        self.pulls: Pulls = Pulls(client)

    def get_by_name(self, name: str) -> Optional[Subreddit]:
        try:
            root = self._client.request('GET', f'/r/{name}/about')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        if root['kind'] == 'Listing':
            return None
        return load_subreddit(root['data'], self._client)

    def fetch_by_name(self, name: str) -> Subreddit:
        root = self._client.request('GET', f'/r/{name}/about')
        if root['kind'] == 'Listing':
            raise exceptions.NoResultException('target not found')
        return load_subreddit(root['data'], self._client)

    def get_potentially_inaccessible_subreddit_by_name(self, name: str) -> Optional[object]:
        root = self._client.request('GET', '/api/info', params={'sr_name': name})
        if children := root['data']['children']:
            return load_potentially_inaccessible_subreddit(children[0]['data'], self._client)
        return None

    def fetch_potentially_inaccessible_subreddit_by_name(self, name: str) -> object:
        v = self.get_potentially_inaccessible_subreddit_by_name(name)
        if v is None:
            raise exceptions.NoResultException('target not found')
        return v

    def bulk_fetch_potentially_inaccessible_subreddits(self, ids: Iterable[int]) -> CallChunkChainingIterator[object]:
        def mass_fetch(ids: Sequence[int]) -> Sequence[object]:
            id36s = map(to_base36, ids)
            full_id36s = map('t5_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_potentially_inaccessible_subreddit(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingIterator(CallChunk(mass_fetch, chunk) for chunk in chunked(ids, 100))

    def bulk_fetch_potentially_inaccessible_subreddits_by_name(self, names: Iterable[str]) -> CallChunkChainingIterator[object]:
        def mass_fetch(names: Sequence[str]) -> Sequence[object]:
            root = self._client.request('GET', '/api/info', params={'sr_name': ','.join(names)})
            return [load_potentially_inaccessible_subreddit(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingIterator(CallChunk(mass_fetch, chunk) for chunk in chunked(names, 100))

    def pull_new_comments(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[LooseCommentListingPaginator, LooseComment]:
        p = LooseCommentListingPaginator(self._client, f'/r/{sr}/comments')
        return ImpartedPaginatorChainingIterator(p, amount)

    def get_settings(self, sr: str) -> Mapping[str, Any]:
        root = self._client.request('GET', f'/r/{sr}/about/edit')
        if root['kind'] != 'subreddit_settings':
            raise exceptions.NoResultException('target not found')
        return root['data']

    def update_settings(self, data: Mapping[str, Any]) -> None:
        self._client.request('PATCH', '/api/v1/subreddit/update_settings', json=data)

    def subscribe_by_name(self, sr: str) -> None:
        self._client.request('POST', '/api/subscribe', data={'action': 'sub', 'sr_name': sr})

    def subscribe_by_id(self, idn: int) -> None:
        id36 = to_base36(idn)
        full_id36 = 't5_' + id36
        self._client.request('POST', '/api/subscribe', data={'action': 'sub', 'sr': full_id36})

    def unsubscribe_by_name(self, sr: str) -> None:
        self._client.request('POST', '/api/subscribe', data={'action': 'unsub', 'sr_name': sr})

    def unsubscribe_by_id(self, idn: int) -> None:
        id36 = to_base36(idn)
        full_id36 = 't5_' + id36
        self._client.request('POST', '/api/subscribe', data={'action': 'unsub', 'sr': full_id36})

    def get_rules(self, sr: str) -> SubredditRules:
        root = self._client.request('GET', f'/r/{sr}/about/rules')
        if 'rules' not in root:
            raise exceptions.NoResultException('target not found')
        return load_subreddit_rules(root)

    def get_post_requirements(self, sr: str) -> Mapping[str, Any]:
        return self._client.request('GET', f'/api/v1/{sr}/post_requirements')

    def search(self, query: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[SubredditSearchPaginator, Subreddit]:
        if not query:
            raise ValueError('query cannot be empty')
        p = SubredditSearchPaginator(self._client, '/subreddits/search', query)
        return ImpartedPaginatorChainingIterator(p, amount)

    def search_names(self, name: str) -> Sequence[str]:
        root = self._client.request('GET', '/api/search_reddit_names', params={'query': name})
        return root['names']

    def exists(self, name: str) -> bool:
        try:
            self._client.request('GET', '/api/search_reddit_names', params={'query': name, 'exact': '1'})
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return False
            raise
        return True

    def get_similar_subreddits(self, sr_id: int, n: Optional[int] = None) -> Sequence[Subreddit]:
        params = {'sr_fullnames': 't5_' + to_base36(sr_id)}
        if n is not None:
            params['max_recs'] = str(n)
        root = self._client.request('GET', '/api/similar_subreddits', params=params)
        return [load_subreddit(d['data'], client=self._client) for d in root['data']['children']]
