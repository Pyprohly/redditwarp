
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, TypeVar, Sequence
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .pushshift_paginator import PushshiftPaginator, PushshiftDocumentPaginator, PushshiftDocumentIDPaginator
from ..models.pushshift_document import PushshiftDocument

T = TypeVar('T')

class SubmissionSearchPaginatorMixin(PushshiftPaginator[T]):
    _query: str
    _query_exclude: str
    _query_title: str
    _query_title_exclude: str
    _query_body: str
    _query_body_exclude: str
    _author: str
    _subreddit: str

    def generate_doseq_params(self) -> Iterable[tuple[str, Sequence[str]]]:
        yield from super().generate_doseq_params()
        if self._query:
            yield ('q', (self._query,))
        if self._query_exclude:
            yield ('q:not', (self._query_exclude,))
        if self._query_title:
            yield ('title', (self._query_title,))
        if self._query_title_exclude:
            yield ('title:not', (self._query_title_exclude,))
        if self._query_body:
            yield ('selftext', (self._query_body,))
        if self._query_body_exclude:
            yield ('selftext:not', (self._query_body_exclude,))
        if self._author:
            yield ('author', (self._author,))
        if self._subreddit:
            yield ('subreddit', (self._subreddit,))



class SubmissionSearchDocumentPaginator(
    SubmissionSearchPaginatorMixin[PushshiftDocument],
    PushshiftDocumentPaginator,
):
    def __init__(self,
        *,
        client: Client,
        url: str,
        limit: Optional[int] = 100,
        after: Optional[int] = None,
        before: Optional[int] = None,
        descending: bool = False,
        fields: Iterable[str] = (),
        query: str = '',
        query_exclude: str = '',
        query_title: str = '',
        query_title_exclude: str = '',
        query_body: str = '',
        query_body_exclude: str = '',
        author: str = '',
        subreddit: str = '',
    ) -> None:
        super().__init__(
            client=client,
            url=url,
            limit=limit,
            after=after,
            before=before,
            descending=descending,
            fields=fields,
        )
        self._query: str = query
        self._query_exclude: str = query_exclude
        self._query_title: str = query_title
        self._query_title_exclude: str = query_title_exclude
        self._query_body: str = query_body
        self._query_body_exclude: str = query_body_exclude
        self._author: str = author
        self._subreddit: str = subreddit

class SubmissionSearchDocumentIDPaginator(
    SubmissionSearchPaginatorMixin[int],
    PushshiftDocumentIDPaginator,
):
    def __init__(self,
        *,
        client: Client,
        url: str,
        limit: Optional[int] = 100,
        after: Optional[int] = None,
        before: Optional[int] = None,
        descending: bool = False,
        query: str = '',
        query_exclude: str = '',
        query_title: str = '',
        query_title_exclude: str = '',
        query_body: str = '',
        query_body_exclude: str = '',
        author: str = '',
        subreddit: str = '',
    ) -> None:
        super().__init__(
            client=client,
            url=url,
            limit=limit,
            after=after,
            before=before,
            descending=descending,
        )
        self._query: str = query
        self._query_exclude: str = query_exclude
        self._query_title: str = query_title
        self._query_title_exclude: str = query_title_exclude
        self._query_body: str = query_body
        self._query_body_exclude: str = query_body_exclude
        self._author: str = author
        self._subreddit: str = subreddit
