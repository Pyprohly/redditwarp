
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Collection, Optional, Sequence
if TYPE_CHECKING:
    from ..client_SYNC import Client

from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...pagination.paginator_chaining_iterator import PaginatorChainingIterator
from ...util.base_conversion import to_base36
from ...iterators.call_chunk import CallChunk
from ...iterators.chunking import chunked
from ..paginators.document_paginator import DocumentPaginator
from ..models.document import Document


class Procedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def bulk_fetch_submissions(self, ids: Iterable[int], *, fields: Optional[Collection[str]] = None) -> CallChunkChainingIterator[Document]:
        """Bulk fetch submission documents by ID.

        .. .PARAMETERS

        :param `Iterable[int]` ids:
            Submission IDs.
        :param `Optional[Collection[str]]` fields:
            Return only specific fields.

        .. .RETURNS

        :rtype: `~.iterators.call_chunk_chaining_iterator.CallChunkChainingIterator`\\[:class:`~.pushshift.models.document.Document`]
        """
        def mass_fetch_submissions(ids: Sequence[int]) -> Sequence[Document]:
            def g() -> Iterable[tuple[str, str]]:
                yield ('limit', '1000')
                yield ('ids', ','.join(map(to_base36, ids)))
                if fields: yield ('fields', ','.join(fields))
            root = self._client.request('GET', '/reddit/submission/search', params=dict(g()))
            return [Document(d) for d in root['data']]

        return CallChunkChainingIterator(CallChunk(mass_fetch_submissions, chunk) for chunk in chunked(ids, 1000))

    def count_search_submissions(self,
        *,
        query: Optional[str] = None,
        query_title: Optional[str] = None,
        query_body: Optional[str] = None,
        subreddit: Optional[str] = None,
        author: Optional[str] = None,
        time_range: Optional[tuple[Optional[int], Optional[int]]] = None,
        since: Optional[int] = None,
        until: Optional[int] = None,
    ) -> int:
        """Return the number of expected entries for a submission search.

        .. .PARAMETERS

        :(parameters): Similar to :meth:`.page_search_submissions`.

        .. .RETURNS

        :rtype: `int`
        """
        if time_range is not None:
            if (since, until) != (None, None):
                raise TypeError("`time_range` cannot be used with `since` or `until`")
            since, until = time_range

        def g() -> Iterable[tuple[str, str]]:
            yield ('track_total_hits', '1')
            yield ('limit', '0')
            if query is not None: yield ('q', query)
            if query_title is not None: yield ('title', query_title)
            if query_body is not None: yield ('selftext', query_body)
            if subreddit is not None: yield ('subreddit', subreddit)
            if author is not None: yield ('author', author)
            if since is not None: yield ('since', str(since))
            if until is not None: yield ('until', str(until))

        root = self._client.request('GET', '/reddit/submission/search', params=dict(g()))
        return root['metadata']['es']['hits']['total']['value']

    def page_search_submissions(self,
        *,
        query: Optional[str] = None,
        query_title: Optional[str] = None,
        query_body: Optional[str] = None,
        subreddit: Optional[str] = None,
        author: Optional[str] = None,
        time_range: Optional[tuple[Optional[int], Optional[int]]] = None,
        since: Optional[int] = None,
        until: Optional[int] = None,
        fields: Optional[Collection[str]] = None,
        descending: bool = False,
    ) -> DocumentPaginator:
        """Return a paginator for a submission search.

        .. .PARAMETERS

        :param `Optional[str]` query:
            Filter by title and body.
        :param `Optional[str]` query_title:
            Filter by title.
        :param `Optional[str]` query_body:
            Filter by body.
        :param `Optional[str]` subreddit:
            Filter by specific subreddits.

            A comma-separated list is accepted.
        :param `Optional[str]` author:
            Filter by specific authors.

            A comma-separated list is accepted.
        :param `Optional[tuple[Optional[int], Optional[int]]]` time_range:
            Filter by time.

            Takes a time range tuple of (since, until).

            The `until` value should always be greater than `since`.

            This parameter cannot be used with `since` or `until`.
        :param `Optional[int]` since:
        :param `Optional[int]` until:
        :param `Optional[Collection[str]]` fields:
            Return only specific fields.

            Values `id` and `created_utc` MUST be included otherwise
            the pagination logic will error out.
        :param `Optional[str]` descending:
            Return results in descending order.

            Note, this only controls the order of the entries according to the
            `created_utc` field and not the `id` field. The order of `id`\\ s is
            never guarented. This means that if you collect, reverse and compare
            the order of entries' `id` fields with a different `descending` value,
            they may not be equal.

        .. .RETURNS

        :rtype: :class:`~.pushshift.paginators.document_paginator.DocumentPaginator`
        """
        return DocumentPaginator(
            client=self._client,
            url='/reddit/submission/search',
            query=query,
            query_title=query_title,
            query_body=query_body,
            subreddit=subreddit,
            author=author,
            time_range=time_range,
            since=since,
            until=until,
            fields=fields,
            descending=descending,
        )

    def pull_search_submissions(self,
        *,
        amount: Optional[int] = None,
        query: Optional[str] = None,
        query_title: Optional[str] = None,
        query_body: Optional[str] = None,
        subreddit: Optional[str] = None,
        author: Optional[str] = None,
        time_range: Optional[tuple[Optional[int], Optional[int]]] = None,
        since: Optional[int] = None,
        until: Optional[int] = None,
        fields: Optional[Collection[str]] = None,
        descending: bool = False,
    ) -> PaginatorChainingIterator[Document]:
        """Pull entries from a submission search.

        Using a paginator object directly is generally recommended.
        I.e., :meth:`.page_search_submissions` is preferred over this method.
        """
        paginator = self.page_search_submissions(
            query=query,
            query_title=query_title,
            query_body=query_body,
            subreddit=subreddit,
            author=author,
            time_range=time_range,
            since=since,
            until=until,
            fields=fields,
            descending=descending,
        )
        return PaginatorChainingIterator(paginator, amount=amount)


    def bulk_fetch_comments(self, ids: Iterable[int], *, fields: Optional[Collection[str]] = None) -> CallChunkChainingIterator[Document]:
        """Bulk fetch comment documents by ID.

        Behaves similarly to :meth:`.bulk_fetch_submissions`.
        """
        def mass_fetch_comments(ids: Sequence[int]) -> Sequence[Document]:
            def g() -> Iterable[tuple[str, str]]:
                yield ('limit', '1000')
                yield ('ids', ','.join(map(to_base36, ids)))
                if fields: yield ('fields', ','.join(fields))
            root = self._client.request('GET', '/reddit/comment/search', params=dict(g()))
            return [Document(d) for d in root['data']]

        return CallChunkChainingIterator(CallChunk(mass_fetch_comments, chunk) for chunk in chunked(ids, 1000))

    def count_search_comments(self,
        *,
        query: Optional[str] = None,
        query_title: Optional[str] = None,
        query_body: Optional[str] = None,
        subreddit: Optional[str] = None,
        author: Optional[str] = None,
        time_range: Optional[tuple[Optional[int], Optional[int]]] = None,
        since: Optional[int] = None,
        until: Optional[int] = None,
    ) -> int:
        """Return the number of expected entries for a submission search.

        Behaves similarly to :meth:`.count_search_submissions`.
        """
        if time_range is not None:
            if (since, until) != (None, None):
                raise TypeError("`time_range` cannot be used with `since` or `until`")
            since, until = time_range

        def g() -> Iterable[tuple[str, str]]:
            yield ('track_total_hits', '1')
            yield ('limit', '0')
            if query is not None: yield ('q', query)
            if query_title is not None: yield ('title', query_title)
            if query_body is not None: yield ('selftext', query_body)
            if subreddit is not None: yield ('subreddit', subreddit)
            if author is not None: yield ('author', author)
            if since is not None: yield ('since', str(since))
            if until is not None: yield ('until', str(until))

        root = self._client.request('GET', '/reddit/comment/search', params=dict(g()))
        return root['metadata']['es']['hits']['total']['value']

    def page_search_comments(self,
        *,
        query: Optional[str] = None,
        query_title: Optional[str] = None,
        query_body: Optional[str] = None,
        subreddit: Optional[str] = None,
        author: Optional[str] = None,
        time_range: Optional[tuple[Optional[int], Optional[int]]] = None,
        since: Optional[int] = None,
        until: Optional[int] = None,
        fields: Optional[Collection[str]] = None,
        descending: bool = False,
    ) -> DocumentPaginator:
        """Return a paginator for a comment search.

        Behaves similarly to :meth:`.page_search_submissions`.
        """
        return DocumentPaginator(
            client=self._client,
            url='/reddit/comment/search',
            query=query,
            query_title=query_title,
            query_body=query_body,
            subreddit=subreddit,
            author=author,
            time_range=time_range,
            since=since,
            until=until,
            fields=fields,
            descending=descending,
        )

    def pull_search_comments(self,
        *,
        amount: Optional[int] = None,
        query: Optional[str] = None,
        query_title: Optional[str] = None,
        query_body: Optional[str] = None,
        subreddit: Optional[str] = None,
        author: Optional[str] = None,
        time_range: Optional[tuple[Optional[int], Optional[int]]] = None,
        since: Optional[int] = None,
        until: Optional[int] = None,
        fields: Optional[Collection[str]] = None,
        descending: bool = False,
    ) -> PaginatorChainingIterator[Document]:
        """Pull entries from a comment search.

        Behaves similarly to :meth:`.pull_search_submissions`.
        """
        paginator = self.page_search_comments(
            query=query,
            query_title=query_title,
            query_body=query_body,
            subreddit=subreddit,
            author=author,
            time_range=time_range,
            since=since,
            until=until,
            fields=fields,
            descending=descending,
        )
        return PaginatorChainingIterator(paginator, amount=amount)