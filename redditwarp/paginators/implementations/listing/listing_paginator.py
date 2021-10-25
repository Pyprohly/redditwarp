
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Any, Mapping, Optional, Callable, Iterable
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ...exceptions import MissingCursorException
from ...bidirectional_cursor_paginator import BidirectionalCursorPaginator

T = TypeVar('T')

class ListingPaginator(BidirectionalCursorPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        params: Optional[Mapping[str, str]] = None,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(limit=limit)
        self.client: Client = client
        self.uri: str = uri
        self.params: Mapping[str, str] = {} if params is None else params
        self.cursor_extractor: Callable[[Any], str] = cursor_extractor
        self.after_count: int = 0
        self.before_count: int = 0
        self.show_all: bool = False

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from self.params.items()

        if self.limit is not None:
            yield ('limit', str(self.limit))
        if self.show_all:
            yield ('show', 'all')

        if self.direction:
            if self.after_count != 0:
                yield ('count', str(self.after_count))

            if self.after:
                yield ('after', self.after)
            elif not self.has_after:
                raise MissingCursorException('after')
        else:
            if self.before_count != 0:
                yield ('count', str(self.before_count))

            if self.before:
                yield ('before', self.before)
            elif not self.has_before:
                raise MissingCursorException('before')

    def _fetch_data(self) -> Mapping[str, Any]:
        params = dict(self._generate_params())
        root = self.client.request('GET', self.uri, params=params)
        return root['data']

    def _process_data(self, data: Mapping[str, Any]) -> None:
        children = data['children']

        dist: int = x if (x := data['dist']) else len(children)
        if self.direction:
            self.after_count += dist
        else:
            self.after_count -= dist
        self.before_count = self.after_count - dist + 1

        after = data['after'] or ''
        before = data['before'] or ''
        if children:
            self.after: str = after if after else self.cursor_extractor(children[-1])
            self.before: str = before if before else self.cursor_extractor(children[0])

        self.has_after: bool = bool(after)
        self.has_before: bool = bool(before)

    def _next_data(self) -> Mapping[str, Any]:
        data = self._fetch_data()
        self._process_data(data)
        return data
