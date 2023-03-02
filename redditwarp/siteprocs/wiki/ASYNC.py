
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

    class Page:
        def __init__(self, outer: WikiProcedures) -> None:
            self._outer = outer
            self._client = outer._client

        async def read(self, sr: str, page: str) -> WikiPage:
            """Get a wiki page.

            .. .PARAMETERS

            :param `str` sr:
            :param `str` page:

            .. .RETURNS

            :rtype: :class:`~.models.wiki_ASYNC.WikiPage`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `PAGE_NOT_FOUND`:
                    The specified wiki page does not exist.
                + `INVALID_REVISION`:
                    The specified revision UUID does not exist.
                + `private`:
                    You do not have access to the specified subreddit; it is private.
                + `banned`:
                    You do not have access to the specified subreddit; it is banned.
            """
            root = await self._client.request('GET', f'/r/{sr}/wiki/{page}')
            return load_wiki_page(root['data'], self._client)

        async def edit(self, sr: str, page: str, body: str, *, message: str = '') -> None:
            """Edit a wiki page.

            If the specifed content matches the current content of the wiki page,
            the edit will not go through.

            .. .PARAMETERS

            :param `str` sr:
            :param `str` page:
            :param `str` body:
            :param `str` message:
                A commit message.

            .. .RETURNS

            :rtype: `None`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `WIKI_CREATE_ERROR`:
                    The specified wiki page does not exist.
                + `private`:
                    You do not have access to the specified subreddit; it is private.
                + `banned`:
                    You do not have access to the specified subreddit; it is banned.
            """
            await self._client.request('POST', f'/r/{sr}/api/wiki/edit',
                    data={'page': page, 'content': body, 'reason': message})

        async def revert(self, sr: str, page: str, revision: str) -> None:
            """Revert a wiki page to a previous revision.

            This creates a new edit with content matching that of the specified revision.

            The revision message will look something like 'reverted back 53 minutes'.

            .. .PARAMETERS

            :param `str` sr:
            :param `str` page:
            :param `str` revision:

            .. .RETURNS

            :rtype: `None`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `INVALID_REVISION`:
                    The specified revision UUID does not exist.
            """
            await self._client.request('POST', f'/r/{sr}/api/wiki/revert',
                    data={'page': page, 'revision': revision})

        def revisions(self, sr: str, page: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[WikiPageRevisionsAsyncPaginator, WikiPageRevision]:
            """Get wiki page revision log entries.

            .. .PARAMETERS

            :param `str` sr:
            :param `str` page:
            :param `Optional[int]` amount:

            .. .RETURNS

            :rtype: :class:`~.pagination.paginator_chaining_async_iterator.ImpartedPaginatorChainingAsyncIterator`[:class:`~.pagination.paginators.wiki_async1.WikiPageRevisionsAsyncPaginator`, :class:`~.models.wiki_ASYNC.WikiPageRevision`]

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `WIKI_DISABLED`:
                    The specified subreddit does not have wikis enabled.
                + `PAGE_NOT_FOUND`:
                    The specified wiki page does not exist.
                + `private`:
                    You do not have access to the specified subreddit; it is private.
                + `banned`:
                    You do not have access to the specified subreddit; it is banned.
            """
            p = WikiPageRevisionsAsyncPaginator(self._client, f'/r/{sr}/wiki/revisions/{page}')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        def discussions(self, sr: str, page: str, amount: Optional[int] = None,
                ) -> ImpartedPaginatorChainingAsyncIterator[SubmissionListingAsyncPaginator, Submission]:
            """Get link submissions linking to a particular wiki page.

            .. .PARAMETERS

            :param `str` sr:
            :param `str` page:
            :param `Optional[int]` amount:

            .. .RETURNS

            :rtype: :class:`~.pagination.paginator_chaining_async_iterator.ImpartedPaginatorChainingAsyncIterator`[:class:`~.pagination.paginators.wiki_async1.SubmissionListingAsyncPaginator`, :class:`~.models.wiki_ASYNC.WikiPageRevision`]

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `WIKI_DISABLED`:
                    The specified subreddit does not have wikis enabled.
                + `PAGE_NOT_FOUND`:
                    The specified wiki page does not exist.
                + `private`:
                    You do not have access to the specified subreddit; it is private.
                + `banned`:
                    You do not have access to the specified subreddit; it is banned.
            """
            p = SubmissionListingAsyncPaginator(self._client, f'/r/{sr}/wiki/discussions/{page}')
            return ImpartedPaginatorChainingAsyncIterator(p, amount)

        async def get_settings(self, sr: str, page: str) -> WikiPageSettings:
            """Retrieve the current permission settings for a wiki page.

            .. .PARAMETERS

            :param `str` sr:
            :param `str` page:

            .. .RETURNS

            :rtype: `~.models.wiki_ASYNC.WikiPageSettings`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `MOD_REQUIRED`:
                    You are not a moderator of the specified subreddit.
                + `WIKI_DISABLED`:
                    The specified subreddit does not have wikis enabled.
                + `PAGE_NOT_FOUND`:
                    The specified wiki page does not exist.
                + `private`:
                    You do not have access to the specified subreddit; it is private.
                + `banned`:
                    You do not have access to the specified subreddit; it is banned.
            """
            root = await self._client.request('GET', f'/r/{sr}/wiki/settings/{page}')
            return load_wiki_page_settings(root['data'], self._client)

        async def set_settings(self, sr: str, page: str, *, permlevel: int, indexed: bool) -> WikiPageSettings:
            """Update the permissions and visibility of a particular wiki page.

            .. .PARAMETERS

            :param `str` sr:
            :param `str` page:
            :param `int` permlevel:
                Permission level indicating who can edit this wiki page.

                "who can edit this page?"

                `0`: "use subreddit wiki permissions"
                `1`: "only approved wiki contributors for this page may edit"
                `2`: "only mods may edit and view"
            :param `bool` indexed:
                Whether this wiki page is to be indexed on the wiki page list.

            .. .RETURNS

            :rtype: `~.models.wiki_ASYNC.WikiPageSettings`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `WIKI_DISABLED`:
                    The specified subreddit does not have wikis enabled.
                + `PAGE_NOT_FOUND`:
                    The specified wiki page does not exist.
                + `private`:
                    You do not have access to the specified subreddit; it is private.
                + `banned`:
                    You do not have access to the specified subreddit; it is banned.
            :raises redditwarp.http.exceptions.StatusCodeException:
                + `302`:
                    You do not have permission.
            """
            root = await self._client.request('POST', f'/r/{sr}/wiki/settings/{page}',
                    data={'permlevel': str(permlevel), 'listed': '01'[indexed]})
            return load_wiki_page_settings(root['data'], self._client)

        async def add_editor(self, sr: str, page: str, username: str) -> None:
            """Add a user as an editor for a wiki page.

            If the user is already added, it is treated as a success.

            .. .PARAMETERS

            :param `str` sr:
            :param `str` page:
            :param `str` username:

            .. .RETURNS

            :rtype: `None`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `WIKI_DISABLED`:
                    The specified subreddit does not have wikis enabled.
                + `UNKNOWN_USER`:
                    The specified user does not exist.
                + `private`:
                    You do not have access to the specified subreddit; it is private.
                + `banned`:
                    You do not have access to the specified subreddit; it is banned.
            """
            await self._client.request('POST', f'/r/{sr}/api/wiki/alloweditor/add', data={'username': username})

        async def remove_editor(self, sr: str, page: str, username: str) -> None:
            """Remove a user as an editor for a wiki page.

            Behaves similarly to :meth:`.add_editor`.
            """
            await self._client.request('POST', f'/r/{sr}/api/wiki/alloweditor/del', data={'username': username})

    page: cached_property[Page] = cached_property(Page)

    def revisions(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[WikiPageRevisionsAsyncPaginator, WikiPageRevision]:
        """Get a revision log for all wiki pages.

        .. .PARAMETERS

        :param `str` sr:
        :param `Optional[int]` amount:

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_async_iterator.ImpartedPaginatorChainingAsyncIterator`[:class:`~.pagination.paginators.wiki_async1.WikiPageRevisionsAsyncPaginator`, :class:`~.models.wiki_ASYNC.WikiPageRevision`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `WIKI_DISABLED`:
                The specified subreddit does not have wikis enabled.
            + `private`:
                You do not have access to the specified subreddit; it is private.
            + `banned`:
                You do not have access to the specified subreddit; it is banned.
        """
        p = WikiPageRevisionsAsyncPaginator(self._client, f'/r/{sr}/wiki/revisions')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def list_pages(self, sr: str) -> Sequence[str]:
        """Get a list of wiki pages in a subreddit.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `Sequence`\\[`str`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `private`:
                You do not have access to the specified subreddit; it is private.
            + `banned`:
                You do not have access to the specified subreddit; it is banned.
        """
        root = await self._client.request('GET', f'/r/{sr}/wiki/pages')
        return root['data']

    async def toggle_revision_hidden(self, sr: str, page: str, revision: str) -> bool:
        """Toggle the public visibility of a wiki page revision.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` page:
        :param `str` revision:

        .. .RETURNS

        :rtype: `Sequence`\\[`str`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `PAGE_NOT_FOUND`:
                The specified wiki page does not exist.
            + `INVALID_REVISION`:
                The specified revision UUID does not exist.
            + `private`:
                You do not have access to the specified subreddit; it is private.
            + `banned`:
                You do not have access to the specified subreddit; it is banned.
        """
        root = await self._client.request('POST', f'/r/{sr}/api/wiki/hide',
                data={'page': page, 'revision': revision})
        return root['status']
