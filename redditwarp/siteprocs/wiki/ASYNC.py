
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_ASYNC import Submission

from functools import cached_property

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.wiki_async1 import WikiPageRevisionsAsyncPaginator
from ...pagination.paginators.listing.submission_listing_async_paginator import SubmissionListingAsyncPaginator
from ...models.wiki_ASYNC import WikiPage, WikiPageRevision, WikiPageSettings
from ...model_loaders.wiki_ASYNC import load_wiki_page, load_wiki_page_settings

class WikiProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    class _page:
        def __init__(self, outer: WikiProcedures) -> None:
            self._outer = outer
            self._client = outer._client

        async def read(self, sr: str, page: str) -> WikiPage:
            root = await self._client.request('GET', f'/r/{sr}/wiki/{page}')
            return load_wiki_page(root['data'], self._client)

        async def edit(self, sr: str, page: str, body: str, *, message: str = '') -> None:
            await self._client.request('POST', f'/r/{sr}/api/wiki/edit',
                    data={'page': page, 'content': body, 'reason': message})

        async def revert(self, sr: str, page: str, revision: str) -> None:
            await self._client.request('POST', f'/r/{sr}/api/wiki/revert',
                    data={'page': page, 'revision': revision})

        def revisions(self, sr: str, page: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[WikiPageRevisionsAsyncPaginator, WikiPageRevision]:
            p = WikiPageRevisionsAsyncPaginator(self._client, f'/r/{sr}/wiki/revisions/{page}')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def discussions(self, sr: str, page: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[SubmissionListingAsyncPaginator, Submission]:
            p = SubmissionListingAsyncPaginator(self._client, f'/r/{sr}/wiki/discussions/{page}')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        async def get_settings(self, sr: str, page: str) -> WikiPageSettings:
            root = await self._client.request('GET', f'/r/{sr}/wiki/settings/{page}')
            return load_wiki_page_settings(root['data'], self._client)

        async def set_settings(self, sr: str, page: str, *, permlevel: int, unlisted: bool) -> WikiPageSettings:
            root = await self._client.request('POST', f'/r/{sr}/wiki/settings/{page}',
                    data={'permlevel': str(permlevel), 'listed': '10'[unlisted]})
            return load_wiki_page_settings(root['data'], self._client)

        async def add_editor(self, sr: str, page: str, username: str) -> None:
            await self._client.request('POST', f'/r/{sr}/api/wiki/alloweditor/add', data={'username': username})

        async def remove_editor(self, sr: str, page: str, username: str) -> None:
            await self._client.request('POST', f'/r/{sr}/api/wiki/alloweditor/del', data={'username': username})

    page: cached_property[_page] = cached_property(_page)

    def revisions(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[WikiPageRevisionsAsyncPaginator, WikiPageRevision]:
        p = WikiPageRevisionsAsyncPaginator(self._client, f'/r/{sr}/wiki/revisions')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def list_pages(self, sr: str) -> Sequence[str]:
        root = await self._client.request('GET', f'/r/{sr}/wiki/pages')
        return root['data']

    async def toggle_revision_hidden(self, sr: str, page: str, revision: str) -> bool:
        root = await self._client.request('POST', f'/r/{sr}/api/wiki/hide',
                data={'page': page, 'revision': revision})
        return root['status']
