
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, TypeVar, Sequence
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .pushshift_paginator import PushshiftPaginator, PushshiftDocumentPaginator, PushshiftDocumentIDPaginator
from ..models.pushshift_document import PushshiftDocument

T = TypeVar('T')

class _CommentSearchPaginatorMixin(PushshiftPaginator[T]):
    _query: str
    _author: str
    _subreddit: str

    def generate_doseq_params(self) -> Iterable[tuple[str, Sequence[str]]]:
        yield from super().generate_doseq_params()
        if self._query:
            yield ('q', (self._query,))
        if self._author:
            yield ('author', (self._author,))
        if self._subreddit:
            yield ('subreddit', (self._subreddit,))


class CommentSearchDocumentPaginator(
    _CommentSearchPaginatorMixin[PushshiftDocument],
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
        self._author: str = author
        self._subreddit: str = subreddit

class CommentSearchDocumentIDPaginator(
    _CommentSearchPaginatorMixin[int],
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
        self._author: str = author
        self._subreddit: str = subreddit
