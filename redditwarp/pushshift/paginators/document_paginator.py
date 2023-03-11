
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from collections.abc import Iterable, Collection, Sequence, Set, Mapping
    from ..client_SYNC import Client

from ...pagination.paginator import Paginator
from ..models.document import Document


class DocumentPaginator(Paginator[Document]):
    def __init__(self,
        client: Client,
        url: str,
        *,
        limit: Optional[int] = 1000,
        search_params: Optional[Mapping[str, str]] = None,
        since: Optional[int] = None,
        until: Optional[int] = None,
        fields: Optional[Collection[str]] = None,
        descending: bool = False,
    ) -> None:
        super().__init__(limit=limit)
        self.client: Client = client
        ("")
        self.url: str = url
        ("")
        self._search_params: Mapping[str, str] = {} if search_params is None else search_params
        self._since_cursor: Optional[int] = since
        self._until_cursor: Optional[int] = until
        self._fields: Optional[Collection[str]] = fields
        self._descending: bool = descending
        self._previous_document_ids: Set[int] = set()

    def fetch(self) -> Sequence[Document]:
        def g() -> Iterable[tuple[str, str]]:
            yield ('order', 'desc' if self._descending else 'asc')
            if self.limit is not None: yield ('limit', str(self.limit))
            if self._since_cursor is not None: yield ('since', str(self._since_cursor))
            if self._until_cursor is not None: yield ('until', str(self._until_cursor))
            if self._fields: yield ('filter', ','.join(self._fields))
            yield from self._search_params.items()

        root = self.client.request('GET', self.url, params=dict(g()))
        documents = root['data']

        m = {d['id']: d for d in documents}
        for i in self._previous_document_ids:
            m.pop(i, None)
        self._previous_document_ids = set(m)
        documents = list(m.values())

        # If this is true then we could be losing some results unless we
        # increase the fetch limit. But the pagination algorithm shouldn't
        # alter the limit so just carry on and try our best.
        all_from_same_time_bucket: bool = len(set(d['created_utc'] for d in documents)) == 1

        if documents:
            cursor: int = documents[-1]['created_utc']
            if self._descending:
                if (self._until_cursor is None) or cursor < self._until_cursor:
                    self._until_cursor = cursor + 1
                if all_from_same_time_bucket:
                    self._until_cursor -= 1
            else:
                if (self._since_cursor is None) or cursor > self._since_cursor:
                    self._since_cursor = cursor
                if all_from_same_time_bucket:
                    self._since_cursor += 1

        return [Document(d) for d in documents]
