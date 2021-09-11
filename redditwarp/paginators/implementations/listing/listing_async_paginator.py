
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Any, Mapping, Optional, Callable, Iterable
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ...exceptions import MissingCursorException
from ...bidirectional_cursor_async_paginator import BidirectionalCursorAsyncPaginator

T = TypeVar('T')

class ListingAsyncPaginator(BidirectionalCursorAsyncPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        params: Optional[Mapping[str, Optional[str]]] = None,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(limit=limit)
        self.client = client
        self.uri = uri
        self.params = {} if params is None else params
        self.cursor_extractor = cursor_extractor
        self.count = 0
        self.show_all = False

    def _generate_params(self) -> Iterable[tuple[str, Optional[str]]]:
        yield from self.params.items()
        yield ('count', str(self.count))
        if self.limit is not None:
            yield ('limit', str(self.limit))
        if self.show_all:
            yield ('show', 'all')

        if self.direction:
            if self.after:
                yield ('after', self.after)
            elif not self.has_after:
                raise MissingCursorException('after')
        else:
            if self.before:
                yield ('before', self.before)
            elif not self.has_before:
                raise MissingCursorException('before')

    async def _fetch_data(self) -> Mapping[str, Any]:
        params = dict(self._generate_params())
        root = await self.client.request('GET', self.uri, params=params)
        return root['data']

    def process_data(self, data: Mapping[str, Any]) -> None:
        children = data['children']

        self.count += z if (z := data['dist']) else len(children)

        after = data['after'] or ''
        before = data['before'] or ''
        if children:
            self.after = after if after else self.cursor_extractor(children[-1])
            self.before = before if before else self.cursor_extractor(children[0])

        self.has_after = bool(after)
        self.has_before = bool(before)

    async def _next_data(self) -> Mapping[str, Any]:
        data = await self._fetch_data()
        self.process_data(data)
        return data
