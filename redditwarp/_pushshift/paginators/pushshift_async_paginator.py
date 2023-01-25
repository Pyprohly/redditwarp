
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, Any, TypeVar
if TYPE_CHECKING:
    from ..client_ASYNC import Client

import urllib.parse

from ...pagination.async_paginator import AsyncPaginator
from ..models.pushshift_document import PushshiftDocument

class MissingExpectedFieldException(Exception):
    pass


T = TypeVar('T')

class PushshiftAsyncPaginator(AsyncPaginator[T]):
    def __init__(self,
        *,
        client: Client,
        url: str,
        limit: Optional[int] = 100,
        after: Optional[int] = None,
        before: Optional[int] = None,
        descending: bool = False,
        fields: Iterable[str] = (),
    ) -> None:
        super().__init__(limit=limit)
        self.client: Client = client
        self.url: str = url
        self._descending: bool = descending
        self._fields: Iterable[str] = fields
        self._time_initial_after: Optional[int] = after
        self._time_initial_before: Optional[int] = before
        self._before_created_utc: Optional[int] = None
        self._after_created_utc: Optional[int] = None
        self._previous_page_item_ids: Sequence[int] = ()

    def generate_doseq_params(self) -> Iterable[tuple[str, Sequence[str]]]:
        if self.limit is not None:
            yield ('limit', (str(self.limit),))

        after: Optional[int] = self._time_initial_after
        before: Optional[int] = self._time_initial_before
        if self._descending:
            yield ('sort', 'desc')

            if (x := self._before_created_utc) is not None:
                before = x + 1
        else:
            yield ('sort', 'asc')

            if (x := self._after_created_utc) is not None:
                after = x - 1

        if after is not None:
            yield ('after', (str(after),))
        if before is not None:
            yield ('before', (str(before),))

        if self._fields:
            yield ('fields', list(self._fields))

    async def _fetch_data(self) -> Any:
        # Pushshift does not support URL encoded commas in query strings.
        # https://github.com/pushshift/api/issues/26
        query_pairs = list(self.generate_doseq_params())
        query_string = urllib.parse.urlencode(query_pairs, doseq=True)
        url = '%s?%s' % (self.url, query_string)

        root = await self.client.request('GET', url)
        documents = root['data']

        previous_page_item_ids_set = set(self._previous_page_item_ids)
        documents = [
            d
            for d in documents
            if int(d.get('id'), 36) not in previous_page_item_ids_set
        ]
        self._previous_page_item_ids = [
            int(x, 36)
            for d in documents
            if (x := d.get('id')) is not None
        ]

        if documents:
            first_created_utc = documents[0].get('created_utc')
            last_created_utc = documents[-1].get('created_utc')
            new_before_created_utc: Optional[int] = first_created_utc
            new_after_created_utc: Optional[int] = last_created_utc
            if self._descending:
                new_after_created_utc, new_before_created_utc = new_before_created_utc, new_after_created_utc

            if (
                self._before_created_utc is not None and new_before_created_utc is None
                or
                self._after_created_utc is not None and new_after_created_utc is None
            ):
                raise MissingExpectedFieldException('a document is missing the `created_utc` field')

            self._before_created_utc = new_before_created_utc
            self._after_created_utc = new_after_created_utc

        return documents


class PushshiftDocumentAsyncPaginator(PushshiftAsyncPaginator[PushshiftDocument]):
    async def fetch(self) -> Sequence[PushshiftDocument]:
        data = await self._fetch_data()
        return [PushshiftDocument(d) for d in data]

class PushshiftDocumentIDAsyncPaginator(PushshiftAsyncPaginator[int]):
    _FIELDS: Sequence[str] = ('id', 'created_utc')

    def __init__(self,
        *,
        client: Client,
        url: str,
        limit: Optional[int] = 100,
        after: Optional[int] = None,
        before: Optional[int] = None,
        descending: bool = False,
    ) -> None:
        super().__init__(
            client=client,
            url=url,
            limit=limit,
            after=after,
            before=before,
            descending=descending,
            fields=self._FIELDS,
        )

    async def fetch(self) -> Sequence[int]:
        data = await self._fetch_data()
        return [int(d['id'], 36) for d in data]
