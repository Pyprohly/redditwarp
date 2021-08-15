
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
            if not self.after and not self.has_after:
                raise MissingCursorException('after')
            yield ('after', self.after)
        else:
            if not self.before and not self.has_before:
                raise MissingCursorException('before')
            yield ('before', self.before)

    def _fetch_data(self) -> Mapping[str, Any]:
        params = dict(self._generate_params())
        root = self.client.request('GET', self.uri, params=params)
        data = root['data']
        children = data['children']
        self.count += x if (x := data['dist']) else len(children)
        after = data['after'] or ''
        before = data['before'] or ''

        if children:
            self.after = after if after else self.cursor_extractor(children[-1])
            self.before = before if before else self.cursor_extractor(children[0])

        self.has_after = bool(after)
        self.has_before = bool(before)
        return data
