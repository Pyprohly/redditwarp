
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Sequence, TypeVar, Optional
if TYPE_CHECKING:
    from ..client_SYNC import Client

import urllib.parse

from ..paginators.comment_search_paginator import CommentSearchDocumentPaginator, CommentSearchDocumentIDPaginator
from ..paginators.submission_search_paginator import SubmissionSearchDocumentPaginator, SubmissionSearchDocumentIDPaginator
from ..models.pushshift_document import PushshiftDocument
from ...util.base_conversion import to_base36
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk import CallChunk
from ...iterators.chunking import chunked

T = TypeVar('T')

class Procedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def bulk_fetch_comments_by_id(self, ids: Iterable[int]) -> CallChunkChainingIterator[PushshiftDocument]:
        def mass_fetch_comments_by_id(ids: Sequence[int]) -> Sequence[PushshiftDocument]:
            ids_str = ','.join(map(to_base36, ids))
            root = self._client.request('GET', '/reddit/comment/search', params={'ids': ids_str})
            return [PushshiftDocument(d) for d in root['data']]

        return CallChunkChainingIterator(CallChunk(mass_fetch_comments_by_id, chunk) for chunk in chunked(ids, 100))

    def bulk_fetch_comments_by_id_selecting_fields(self, ids: Iterable[int], *, fields: Iterable[str]) -> CallChunkChainingIterator[PushshiftDocument]:
        def mass_fetch_comments_by_id_selecting_fields(ids: Sequence[int]) -> Sequence[PushshiftDocument]:
            params = {
                'ids': ','.join(map(to_base36, ids)),
                'fields': ','.join(fields),
            }
            root = self._client.request('GET', '/reddit/comment/search', params=params)
            return [PushshiftDocument(d) for d in root['data']]

        return CallChunkChainingIterator(CallChunk(mass_fetch_comments_by_id_selecting_fields, chunk) for chunk in chunked(ids, 100))



    def page_search_comments(self,
        query: str = '',
        *,
        author: str = '',
        subreddit: str = '',
        after: Optional[int] = None,
        before: Optional[int] = None,
        descending: bool = False,
    ) -> CommentSearchDocumentPaginator:
        return CommentSearchDocumentPaginator(
            client=self._client,
            url='/reddit/search/comment',
            query=query,
            author=author,
            subreddit=subreddit,
            after=after,
            before=before,
            descending=descending,
        )

    def page_search_comments_select_id(self,
        query: str = '',
        *,
        author: str = '',
        subreddit: str = '',
        after: Optional[int] = None,
        before: Optional[int] = None,
        descending: bool = False,
    ) -> CommentSearchDocumentIDPaginator:
        return CommentSearchDocumentIDPaginator(
            client=self._client,
            url='/reddit/search/comment',
            query=query,
            author=author,
            subreddit=subreddit,
            after=after,
            before=before,
            descending=descending,
        )

    def page_search_comments_selecting_fields(self,
        query: str = '',
        *,
        author: str = '',
        subreddit: str = '',
        after: Optional[int] = None,
        before: Optional[int] = None,
        descending: bool = False,
        fields: Iterable[str],
    ) -> CommentSearchDocumentPaginator:
        return CommentSearchDocumentPaginator(
            client=self._client,
            url='/reddit/search/comment',
            query=query,
            author=author,
            subreddit=subreddit,
            after=after,
            before=before,
            descending=descending,
            fields=fields,
        )

    def count_search_comments(self,
        query: str = '',
        *,
        author: str = '',
        subreddit: str = '',
        after: Optional[int] = None,
        before: Optional[int] = None,
    ) -> int:
        p = self.page_search_comments(
            query=query,
            author=author,
            subreddit=subreddit,
            after=after,
            before=before,
        )
        p.limit = 0
        query_pairs = list(p.generate_doseq_params()) + [('metadata', ('true',))]
        query_string = urllib.parse.urlencode(query_pairs, doseq=True)
        url = '%s?%s' % (p.url, query_string)
        root = self._client.request('GET', url)
        return root['metadata']['total_results']



    def page_search_submissions(self,
        query: str = '',
        *,
        query_exclude: str = '',
        query_title: str = '',
        query_title_exclude: str = '',
        query_body: str = '',
        query_body_exclude: str = '',
        author: str = '',
        subreddit: str = '',
        after: Optional[int] = None,
        before: Optional[int] = None,
        descending: bool = False,
    ) -> SubmissionSearchDocumentPaginator:
        return SubmissionSearchDocumentPaginator(
            client=self._client,
            url='/reddit/search/submission',
            query=query,
            query_exclude=query_exclude,
            query_title=query_title,
            query_title_exclude=query_title_exclude,
            query_body=query_body,
            query_body_exclude=query_body_exclude,
            author=author,
            subreddit=subreddit,
            after=after,
            before=before,
            descending=descending,
        )

    def page_search_submissions_select_id(self,
        query: str = '',
        *,
        query_exclude: str = '',
        query_title: str = '',
        query_title_exclude: str = '',
        query_body: str = '',
        query_body_exclude: str = '',
        author: str = '',
        subreddit: str = '',
        after: Optional[int] = None,
        before: Optional[int] = None,
        descending: bool = False,
    ) -> SubmissionSearchDocumentIDPaginator:
        return SubmissionSearchDocumentIDPaginator(
            client=self._client,
            url='/reddit/search/submission',
            query=query,
            query_exclude=query_exclude,
            query_title=query_title,
            query_title_exclude=query_title_exclude,
            query_body=query_body,
            query_body_exclude=query_body_exclude,
            author=author,
            subreddit=subreddit,
            after=after,
            before=before,
            descending=descending,
        )

    def page_search_submissions_selecting_fields(self,
        query: str = '',
        *,
        query_exclude: str = '',
        query_title: str = '',
        query_title_exclude: str = '',
        query_body: str = '',
        query_body_exclude: str = '',
        author: str = '',
        subreddit: str = '',
        after: Optional[int] = None,
        before: Optional[int] = None,
        descending: bool = False,
        fields: Iterable[str],
    ) -> SubmissionSearchDocumentPaginator:
        return SubmissionSearchDocumentPaginator(
            client=self._client,
            url='/reddit/search/submission',
            query=query,
            query_exclude=query_exclude,
            query_title=query_title,
            query_title_exclude=query_title_exclude,
            query_body=query_body,
            query_body_exclude=query_body_exclude,
            author=author,
            subreddit=subreddit,
            after=after,
            before=before,
            descending=descending,
            fields=fields,
        )

    def count_search_submissions(self,
        query: str = '',
        *,
        query_exclude: str = '',
        query_title: str = '',
        query_title_exclude: str = '',
        query_body: str = '',
        query_body_exclude: str = '',
        author: str = '',
        subreddit: str = '',
        after: Optional[int] = None,
        before: Optional[int] = None,
    ) -> int:
        p = self.page_search_submissions(
            query=query,
            query_exclude=query_exclude,
            query_title=query_title,
            query_title_exclude=query_title_exclude,
            query_body=query_body,
            query_body_exclude=query_body_exclude,
            author=author,
            subreddit=subreddit,
            after=after,
            before=before,
        )
        p.limit = 0
        query_pairs = list(p.generate_doseq_params()) + [('metadata', ('true',))]
        query_string = urllib.parse.urlencode(query_pairs, doseq=True)
        url = '%s?%s' % (p.url, query_string)
        root = self._client.request('GET', url)
        return root['metadata']['total_results']
