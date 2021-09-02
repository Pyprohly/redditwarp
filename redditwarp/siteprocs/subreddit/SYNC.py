
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Sequence, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit as SubredditModel
    from ...models.comment_SYNC import ExtraSubmissionFieldsComment
    from ...models.subreddit_rules import SubredditRules
    from ...models.moderator_list import ModeratorListItem

from ...models.load.subreddit_SYNC import load_subreddit
from ...models.load.subreddit_rules import load_subreddit_rules
from ...models.load.moderator_list import load_moderator_list_item
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk_SYNC import CallChunk
from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...paginators.implementations.listing.user_pull_sync import CommentListingPaginator
from ... import exceptions
from ...http.util.json_load import json_loads_response
from .fetch_SYNC import Fetch
from .get_SYNC import Get
from .pull_SYNC import Pull
from .grab_SYNC import Grab

class Subreddit:
    def __init__(self, client: Client):
        self._client = client
        self.get = Get(client)
        self.fetch = Fetch(client)
        self.pull = Pull(client)
        self.grab = Grab(client)

    def get_by_name(self, name: str) -> Optional[SubredditModel]:
        try:
            root = self._client.request('GET', f'/r/{name}/about')
        except (
            # A special subreddit name (`all`, `popular`, `friends`, `mod`) was specified.
            exceptions.HTTPStatusError,
            # Name contained invalid characters.
            exceptions.UnacceptableHTMLDocumentReceivedError,
        ) as e:
            if e.response.status == 404:
                return None
            raise

        if root['kind'] != 't5':
            # The subreddit was not found.
            return None

        return load_subreddit(root['data'], self._client)

    def fetch_by_name(self, name: str) -> SubredditModel:
        root = self._client.request('GET', f'/r/{name}/about')
        if root['kind'] == 'Listing':
            raise exceptions.NoResultException('target not found')
        return load_subreddit(root['data'], self._client)

    def bulk_fetch(self, ids: Iterable[int]) -> CallChunkChainingIterator[int, SubredditModel]:
        def mass_fetch(ids: Sequence[int]) -> Sequence[SubredditModel]:
            id36s = map(to_base36, ids)
            full_id36s = map('t5_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_subreddit(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingIterator(
                CallChunk(mass_fetch, idfs) for idfs in chunked(ids, 100))

    def pull_new_comments(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[CommentListingPaginator, ExtraSubmissionFieldsComment]:
        p = CommentListingPaginator(self._client, f'/r/{sr}/comments')
        return PaginatorChainingIterator(p, amount)

    def get_settings(self, sr: str) -> Mapping[str, Any]:
        root = self._client.request('GET', f'/r/{sr}/about/edit')
        if root['kind'] != 'subreddit_settings':
            raise exceptions.NoResultException('target not found')
        return root['data']

    def update_settings(self, data: Mapping[str, Any]) -> None:
        self._client.request('PATCH', '/api/v1/subreddit/update_settings', json=data)

    def DEFUNCT__trending_subreddit_names(self) -> Sequence[str]:
        req = self._client.http.session.make_request('GET', 'https://reddit.com/api/trending_subreddits.json')
        resp = self._client.http.send(req)
        jdata = json_loads_response(resp)
        return jdata['subreddit_names']

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

    def search_reddit_names(self, query: str) -> Sequence[str]:
        root = self._client.request('GET', '/api/search_reddit_names', params={'query': query})
        return root['names']

    def subreddit_name_exists(self, name: str) -> bool:
        try:
            self._client.request('GET', '/api/search_reddit_names', params={'query': name, 'exact': '1'})
        except exceptions.HTTPStatusError as e:
            if e.response.status == 404:
                return False
            raise
        return True

    def list_moderators(self, sr: str) -> Sequence[ModeratorListItem]:
        root = self._client.request('GET', f'/r/{sr}/about/moderators')
        return [load_moderator_list_item(d) for d in root['data']['children']]
