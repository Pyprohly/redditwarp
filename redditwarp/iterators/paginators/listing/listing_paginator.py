
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Any, Mapping, MutableMapping, Optional, Callable, Sequence, Iterable
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ..cursor_bidirectional_paginator import CursorBidirectionalPaginator

T = TypeVar('T')

class ListingPaginator(CursorBidirectionalPaginator[T]):
    def __init__(self,
        client: Client,
        path: str,
        *,
        limit: Optional[int] = 100,
        params: Optional[Mapping[str, Optional[str]]] = None,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__()
        self.limit = limit
        self.client = client
        self.path = path
        self.params = {} if params is None else params
        self.cursor_extractor = cursor_extractor
        self.count = 0
        self.show_all = False

    def _get_params(self) -> MutableMapping[str, Optional[str]]:
        def g() -> Iterable[tuple[str, Optional[str]]]:
            yield from self.params.items()
            yield ('count', str(self.count))
            yield ('limit', str(self.limit))
            if self.show_all:
                yield ('show', 'all')
            if self.get_direction():
                if self.forward_cursor:
                    yield ('after', self.forward_cursor)
            else:
                if self.backward_cursor:
                    yield ('before', self.backward_cursor)

        return dict(g())

    def _fetch_data(self) -> Mapping[str, Any]:
        params = self._get_params()
        recv = self.client.request('GET', self.path, params=params)
        data = recv['data']
        self.count += dist if (dist := data['dist']) is not None else len(data['children'])
        entries = data['children']
        after = data['after']
        before = data['before']

        if entries:
            self.forward_cursor = after if after else self.cursor_extractor(entries[-1])
            self.backward_cursor = before if before else self.cursor_extractor(entries[0])

        self.forward_available = bool(after)
        self.backward_available = bool(before)
        return data

    def _fetch_result(self) -> Sequence[T]:
        raise NotImplementedError

    def next_result(self) -> Sequence[T]:
        self.resuming = False
        return self._fetch_result()

    def reset(self) -> None:
        super().reset()
        self.count = 0
