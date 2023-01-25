
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Any, Mapping, Optional, Callable, Iterable
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ...async_paginator import CursorAsyncPaginator, Bidirectional, MoreAvailableAsyncPaginator, Resettable

T = TypeVar('T')

class ListingAsyncPaginator(Resettable, MoreAvailableAsyncPaginator[T], Bidirectional, CursorAsyncPaginator[T]):
    def __init__(self,
        client: Client,
        url: str,
        *,
        limit: Optional[int] = 100,
        params: Optional[Mapping[str, str]] = None,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ) -> None:
        super().__init__(limit=limit)
        self.client: Client = client
        self.url: str = url
        self.params: Mapping[str, str] = {} if params is None else params
        self.cursor_extractor: Callable[[Any], str] = cursor_extractor
        self.direction: bool = True
        self.show_all: bool = False
        self.__reset()

    def __reset(self) -> None:
        self.after: str = ''
        self.before: str = ''
        self.has_after: bool = True
        self.has_before: bool = True
        self.after_count: int = 0
        self.before_count: int = 0

    def reset(self) -> None:
        self.__reset()

    def get_cursor(self) -> str:
        return self.after if self.direction else self.before

    def set_cursor(self, value: str) -> None:
        if self.direction:
            self.after = value
        else:
            self.before = value

    def has_more_available(self) -> bool:
        return self.has_after if self.direction else self.has_before

    def set_has_more_available_flag(self, value: bool) -> None:
        if self.direction:
            self.has_after = value
        else:
            self.has_before = value

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from self.params.items()

        if self.limit is not None:
            yield ('limit', str(self.limit))
        if self.show_all:
            yield ('show', 'all')

        if self.direction:
            if self.after_count:
                yield ('count', str(self.after_count))
            if self.after:
                yield ('after', self.after)
        else:
            if self.before_count:
                yield ('count', str(self.before_count))
            if self.before:
                yield ('before', self.before)

    async def _fetch_data(self) -> Any:
        params = dict(self._generate_params())
        root = await self.client.request('GET', self.url, params=params)
        data = root['data']
        children = data['children']

        dist: int = x if (x := data['dist']) else len(children)
        self.after_count += (1 if self.direction else -1) * dist
        self.before_count = self.after_count - dist + 1

        suggested_forward_cursor = data['after'] or ''
        suggested_backward_cursor = data['before'] or ''
        if children:
            self.after = suggested_forward_cursor if suggested_forward_cursor else self.cursor_extractor(children[-1])
            self.before = suggested_backward_cursor if suggested_backward_cursor else self.cursor_extractor(children[0])
        self.has_after = bool(suggested_forward_cursor)
        self.has_before = bool(suggested_backward_cursor)

        return data
