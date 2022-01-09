
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission

from functools import cached_property

from ...paginators.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...paginators.implementations.wiki_sync import WikiPageRevisionsPaginator
from ...paginators.listing.submission_listing_paginator import SubmissionListingPaginator
from ...models.wiki_SYNC import WikiPage, WikiPageRevision, WikiPageSettings
from ...models.load.wiki_SYNC import load_wiki_page, load_wiki_page_settings

class WikiProcedures:
    def __init__(self, client: Client):
        self._client = client

    class _page:
        def __init__(self, outer: WikiProcedures):
            self._outer = outer
            self._client = outer._client

        def read(self, sr: str, page: str) -> WikiPage:
            root = self._client.request('GET', f'/r/{sr}/wiki/{page}')
            return load_wiki_page(root['data'], self._client)

        def edit(self, sr: str, page: str, body: str, *, message: str = '') -> None:
            self._client.request('POST', f'/r/{sr}/api/wiki/edit',
                    data={'page': page, 'content': body, 'reason': message})

        def revert(self, sr: str, page: str, revision: str) -> None:
            self._client.request('POST', f'/r/{sr}/api/wiki/revert',
                    data={'page': page, 'revision': revision})

        def revisions(self, sr: str, page: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[WikiPageRevisionsPaginator, WikiPageRevision]:
            p = WikiPageRevisionsPaginator(self._client, f'/r/{sr}/wiki/revisions/{page}')
            return ImpartedPaginatorChainingIterator(p, amount)

        def discussions(self, sr: str, page: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingIterator[SubmissionListingPaginator, Submission]:
            p = SubmissionListingPaginator(self._client, f'/r/{sr}/wiki/discussions/{page}')
            return ImpartedPaginatorChainingIterator(p, amount)

        def get_settings(self, sr: str, page: str) -> WikiPageSettings:
            root = self._client.request('GET', f'/r/{sr}/wiki/settings/{page}')
            return load_wiki_page_settings(root['data'], self._client)

        def set_settings(self, sr: str, page: str, *, permlevel: int, unlisted: bool) -> WikiPageSettings:
            root = self._client.request('POST', f'/r/{sr}/wiki/settings/{page}',
                    data={'permlevel': str(permlevel), 'listed': '10'[unlisted]})
            return load_wiki_page_settings(root['data'], self._client)

        def add_editor(self, sr: str, page: str, username: str) -> None:
            self._client.request('POST', f'/r/{sr}/api/wiki/alloweditor/add', data={'username': username})

        def remove_editor(self, sr: str, page: str, username: str) -> None:
            self._client.request('POST', f'/r/{sr}/api/wiki/alloweditor/del', data={'username': username})

    page: cached_property[_page] = cached_property(_page)

    def revisions(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[WikiPageRevisionsPaginator, WikiPageRevision]:
        p = WikiPageRevisionsPaginator(self._client, f'/r/{sr}/wiki/revisions')
        return ImpartedPaginatorChainingIterator(p, amount)

    def list_pages(self, sr: str) -> Sequence[str]:
        root = self._client.request('GET', f'/r/{sr}/wiki/pages')
        return root['data']

    def toggle_revision_hidden(self, sr: str, page: str, revision: str) -> bool:
        root = self._client.request('POST', f'/r/{sr}/api/wiki/hide',
                data={'page': page, 'revision': revision})
        return root['status']
